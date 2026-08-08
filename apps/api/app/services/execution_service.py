from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.core.exceptions import (
    ApprovalRequiredException,
    ArtifactHashMismatchException,
    DuplicateCommandException,
    NotFoundException,
)
from apps.api.app.db.models import (
    Account,
    ApprovalDecision,
    ArtifactManifest,
    BrokerOrder,
    BrokerOrderEvent,
    ExecutionIntent,
    Fill,
    IdempotencyRecord,
    Instrument,
    RecommendationVersion,
    Workflow,
)
from apps.api.app.providers.broker_provider import BrokerProvider
from apps.api.app.services.audit_service import AuditService
from apps.api.app.services.workflow_service import WorkflowService


class ExecutionService:
    @staticmethod
    def execute_approved_intent(
        db: Session,
        tenant_id: UUID,
        actor_id: UUID,
        approved_artifact_id: UUID,
        approved_artifact_hash: str,
        account_id: UUID,
        integration_id: UUID,
        idempotency_key: str,
    ) -> ExecutionIntent:
        """Submit trade execution strictly for a pre-approved recommendation artifact manifest."""
        # 1. Idempotency Check
        existing_idempotency = (
            db.query(IdempotencyRecord)
            .filter(
                IdempotencyRecord.tenant_id == tenant_id,
                IdempotencyRecord.scope == "trade_execution",
                IdempotencyRecord.idempotency_key == idempotency_key,
            )
            .first()
        )
        if existing_idempotency:
            raise DuplicateCommandException(idempotency_key)

        # 2. Revalidate Artifact Manifest & Human Approval Decision
        manifest = (
            db.query(ArtifactManifest)
            .filter(ArtifactManifest.id == approved_artifact_id, ArtifactManifest.tenant_id == tenant_id)
            .first()
        )
        if not manifest:
            raise NotFoundException("ArtifactManifest", approved_artifact_id)

        # Revalidate exact artifact hash
        if approved_artifact_hash != manifest.content_hash:
            raise ArtifactHashMismatchException(
                f"Artifact hash '{approved_artifact_hash}' does not match locked manifest hash '{manifest.content_hash}'."
            )

        # Revalidate active APPROVE decision
        decision = (
            db.query(ApprovalDecision)
            .join(ApprovalDecision.approval_task)
            .filter(
                ApprovalDecision.approval_task.has(artifact_manifest_id=manifest.id),
                ApprovalDecision.decision == "APPROVE",
                ApprovalDecision.revoked_at.is_(None),
            )
            .first()
        )
        if not decision:
            raise ApprovalRequiredException(
                "Execution rejected: No valid active APPROVE decision exists for this artifact manifest."
            )

        workflow = db.query(Workflow).filter(Workflow.id == manifest.workflow_id).first()
        account = db.query(Account).filter(Account.id == account_id, Account.tenant_id == tenant_id).first()
        if not account:
            raise NotFoundException("Account", account_id)

        # 3. Create Execution Intent
        execution_intent = ExecutionIntent(
            tenant_id=tenant_id,
            workflow_id=workflow.id,
            approval_decision_id=decision.id,
            artifact_manifest_id=manifest.id,
            artifact_hash=approved_artifact_hash,
            account_id=account.id,
            integration_id=integration_id,
            idempotency_key=idempotency_key,
            status="SUBMITTED",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(execution_intent)
        db.flush()

        # 4. Process Allocations via BrokerProvider Sandbox
        instruments = {i.id: i for i in db.query(Instrument).all()}
        rec_version = (
            db.query(RecommendationVersion)
            .filter(RecommendationVersion.id == manifest.recommendation_version_id)
            .first()
        )
        allocations = rec_version.allocations if rec_version else []
        total_executed_cash = Decimal("0.0000")

        for alloc in allocations:
            instr = instruments.get(alloc.instrument_id)
            symbol = instr.symbol if instr else "AAPL"
            fix_res = BrokerProvider.submit_fix_order(
                account_number=account.account_number,
                symbol=symbol,
                side=alloc.side,
                quantity=alloc.target_quantity,
            )

            order = BrokerOrder(
                tenant_id=tenant_id,
                execution_intent_id=execution_intent.id,
                instrument_id=alloc.instrument_id,
                client_order_id=fix_res["client_order_id"],
                provider_order_id=fix_res["provider_order_id"],
                side=alloc.side,
                order_type="MARKET",
                quantity=alloc.target_quantity,
                limit_price=fix_res["executed_price_dec"],
                status="FILLED",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            db.add(order)
            db.flush()

            # Record Broker Event
            payload_dict = {
                "client_order_id": fix_res["client_order_id"],
                "provider_order_id": fix_res["provider_order_id"],
                "status": fix_res["status"],
                "executed_quantity": str(fix_res["executed_quantity_dec"]),
                "executed_price": str(fix_res["executed_price_dec"]),
                "venue": fix_res["venue"],
                "execution_id": fix_res["execution_id"],
            }
            event = BrokerOrderEvent(
                broker_order_id=order.id,
                provider_message_id=f"MSG-{fix_res['client_order_id']}",
                sequence_number=1,
                event_type="ORDER_FILLED",
                payload=payload_dict,
                occurred_at=datetime.now(timezone.utc),
            )
            db.add(event)

            # Record Fill
            fill = Fill(
                broker_order_id=order.id,
                execution_id=fix_res["execution_id"],
                quantity=fix_res["executed_quantity_dec"],
                price=fix_res["executed_price_dec"],
                venue=fix_res["venue"],
                executed_at=datetime.now(timezone.utc),
            )
            db.add(fill)

            total_executed_cash += fix_res["executed_quantity_dec"] * fix_res["executed_price_dec"]

        # Deduct cash from Account
        account.available_cash -= total_executed_cash
        execution_intent.status = "EXECUTED"

        # Record Idempotency Record
        idempotency_rec = IdempotencyRecord(
            tenant_id=tenant_id,
            scope="trade_execution",
            idempotency_key=idempotency_key,
            request_hash=approved_artifact_hash,
            resource_type="execution_intent",
            resource_id=execution_intent.id,
            response_code=200,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(idempotency_rec)

        # Transition workflow to PORTFOLIO_MONITORING stage
        WorkflowService.transition_stage(
            db=db,
            workflow=workflow,
            actor_id=actor_id,
            to_stage="PORTFOLIO_MONITORING",
            to_status="RUNNING",
            reason=f"Trade Execution completed successfully across {len(allocations)} order allocations",
        )

        AuditService.record_audit_event(
            db=db,
            tenant_id=tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="USER",
            actor_id=actor_id,
            action="execution.submitted",
            resource_type="execution_intent",
            resource_id=execution_intent.id,
            outcome="SUCCESS",
            payload={
                "execution_intent_id": str(execution_intent.id),
                "artifact_hash": approved_artifact_hash,
                "total_executed_value": str(total_executed_cash),
            },
        )

        db.commit()
        db.refresh(execution_intent)
        return execution_intent
