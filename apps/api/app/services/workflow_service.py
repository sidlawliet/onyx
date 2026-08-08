import uuid
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.core.exceptions import NotFoundException, WorkflowTransitionException
from apps.api.app.db.models import Portfolio, User, Workflow, WorkflowTransition
from apps.api.app.services.audit_service import AuditService


VALID_STAGES = [
    "MARKET_INTELLIGENCE",
    "PORTFOLIO_STRATEGY",
    "HUMAN_APPROVAL",
    "TRADE_EXECUTION",
    "PORTFOLIO_MONITORING",
]

VALID_STAGE_FLOW = {
    "MARKET_INTELLIGENCE": "PORTFOLIO_STRATEGY",
    "PORTFOLIO_STRATEGY": "HUMAN_APPROVAL",
    "HUMAN_APPROVAL": "TRADE_EXECUTION",
    "TRADE_EXECUTION": "PORTFOLIO_MONITORING",
    "PORTFOLIO_MONITORING": "PORTFOLIO_STRATEGY",  # Loop back for rebalance
}


class WorkflowService:
    @staticmethod
    def create_workflow(db: Session, tenant_id: UUID, user_id: UUID, portfolio_id: UUID, title: str) -> Workflow:
        """Create a new 5-stage institutional workflow starting at MARKET_INTELLIGENCE."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.tenant_id == tenant_id).first()
        if not portfolio:
            raise NotFoundException("Portfolio", portfolio_id)

        trace_id = uuid.uuid4()
        workflow = Workflow(
            tenant_id=tenant_id,
            portfolio_id=portfolio_id,
            created_by=user_id,
            trace_id=trace_id,
            title=title,
            stage="MARKET_INTELLIGENCE",
            status="RUNNING",
            version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(workflow)
        db.flush()

        # Record initial transition
        transition = WorkflowTransition(
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            actor_id=user_id,
            from_stage=None,
            to_stage="MARKET_INTELLIGENCE",
            from_status=None,
            to_status="RUNNING",
            reason="Workflow initialized",
            occurred_at=datetime.now(timezone.utc),
        )
        db.add(transition)

        # Audit event & Outbox event
        AuditService.record_audit_event(
            db=db,
            tenant_id=tenant_id,
            trace_id=trace_id,
            workflow_id=workflow.id,
            actor_type="USER",
            actor_id=user_id,
            action="workflow.create",
            resource_type="workflow",
            resource_id=workflow.id,
            outcome="SUCCESS",
            payload={"title": title, "portfolio_id": str(portfolio_id), "stage": "MARKET_INTELLIGENCE"},
        )
        AuditService.publish_outbox_event(
            db=db,
            tenant_id=tenant_id,
            trace_id=trace_id,
            aggregate_type="workflow",
            aggregate_id=workflow.id,
            event_type="WORKFLOW_CREATED",
            payload={"workflow_id": str(workflow.id), "stage": "MARKET_INTELLIGENCE"},
        )

        db.commit()
        db.refresh(workflow)
        return workflow

    @staticmethod
    def transition_stage(
        db: Session,
        workflow: Workflow,
        actor_id: UUID,
        to_stage: str,
        to_status: str = "RUNNING",
        reason: str | None = None,
    ) -> Workflow:
        """Enforce valid workflow stage transitions."""
        if to_stage not in VALID_STAGES:
            raise WorkflowTransitionException(f"Invalid stage '{to_stage}'. Must be one of {VALID_STAGES}.")

        expected_next = VALID_STAGE_FLOW.get(workflow.stage)
        if to_stage != expected_next and to_stage != workflow.stage:
            raise WorkflowTransitionException(
                f"Cannot transition directly from {workflow.stage} to {to_stage}. Next valid stage is {expected_next}."
            )

        from_stage = workflow.stage
        from_status = workflow.status

        workflow.stage = to_stage
        workflow.status = to_status
        workflow.version += 1
        workflow.updated_at = datetime.now(timezone.utc)

        transition = WorkflowTransition(
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            actor_id=actor_id,
            from_stage=from_stage,
            to_stage=to_stage,
            from_status=from_status,
            to_status=to_status,
            reason=reason or f"Transitioned to {to_stage}",
            occurred_at=datetime.now(timezone.utc),
        )
        db.add(transition)

        AuditService.record_audit_event(
            db=db,
            tenant_id=workflow.tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="SYSTEM",
            actor_id=actor_id,
            action="workflow.transition",
            resource_type="workflow",
            resource_id=workflow.id,
            outcome="SUCCESS",
            payload={"from_stage": from_stage, "to_stage": to_stage, "reason": reason},
        )
        return workflow
