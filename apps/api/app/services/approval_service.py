from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.core.exceptions import (
    ArtifactHashMismatchException,
    DomainException,
    NotFoundException,
    WorkflowTransitionException,
)
from apps.api.app.db.models import (
    ApprovalDecision,
    ApprovalTask,
    ArtifactManifest,
    RecommendationVersion,
    User,
    ValidationRun,
    Workflow,
)
from apps.api.app.services.audit_service import AuditService
from apps.api.app.services.workflow_service import WorkflowService


class ApprovalService:
    @staticmethod
    def submit_for_approval(db: Session, recommendation_version_id: UUID, actor_id: UUID) -> ApprovalTask:
        """Submit a validated recommendation to the Human Approval Gate."""
        rec_version = (
            db.query(RecommendationVersion)
            .filter(RecommendationVersion.id == recommendation_version_id)
            .first()
        )
        if not rec_version:
            raise NotFoundException("RecommendationVersion", recommendation_version_id)

        workflow = db.query(Workflow).filter(Workflow.id == rec_version.recommendation.workflow_id).first()

        # Check validation run status
        val_run = (
            db.query(ValidationRun)
            .filter(ValidationRun.recommendation_version_id == rec_version.id)
            .order_by(ValidationRun.completed_at.desc())
            .first()
        )
        if not val_run or val_run.status != "PASS":
            raise DomainException(
                status_code=422,
                code="VALIDATION_REQUIRED",
                message="Recommendation must pass pre-trade mandate validation before submitting for human approval.",
            )

        # 1. Create LOCKED Artifact Manifest
        manifest = ArtifactManifest(
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            recommendation_version_id=rec_version.id,
            schema_version="1.0.0",
            content_hash=rec_version.artifact_hash,
            storage_uri=f"s3://investops-artifacts/{workflow.tenant_id}/{workflow.id}/manifest-v1.json",
            status="LOCKED",
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(days=7),
        )
        db.add(manifest)
        db.flush()

        # Find designated Portfolio Manager approver user
        approver = db.query(User).filter(User.email == "approver@investops.ai").first()
        approver_id = approver.id if approver else actor_id

        # 2. Create Approval Task
        task = ApprovalTask(
            tenant_id=workflow.tenant_id,
            workflow_id=workflow.id,
            artifact_manifest_id=manifest.id,
            assigned_to=approver_id,
            status="PENDING",
            due_at=datetime.now(timezone.utc) + timedelta(hours=24),
            created_at=datetime.now(timezone.utc),
        )
        db.add(task)
        db.flush()

        # Transition workflow to HUMAN_APPROVAL stage
        WorkflowService.transition_stage(
            db=db,
            workflow=workflow,
            actor_id=actor_id,
            to_stage="HUMAN_APPROVAL",
            to_status="AWAITING_REVIEW",
            reason="Recommendation submitted to Human Approval Gate with locked artifact manifest",
        )

        AuditService.record_audit_event(
            db=db,
            tenant_id=workflow.tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="USER",
            actor_id=actor_id,
            action="approval.task_created",
            resource_type="approval_task",
            resource_id=task.id,
            outcome="SUCCESS",
            payload={"task_id": str(task.id), "artifact_hash": rec_version.artifact_hash},
        )

        db.commit()
        db.refresh(task)
        return task

    @staticmethod
    def record_decision(
        db: Session,
        task_id: UUID,
        decided_by: UUID,
        decision: str,
        artifact_hash: str,
        attestation: str | None = None,
        reason: str | None = None,
        mfa_verified: bool = True,
    ) -> ApprovalDecision:
        """Record explicit human approval decision (APPROVE, REJECT, or MODIFY)."""
        task = db.query(ApprovalTask).filter(ApprovalTask.id == task_id).first()
        if not task:
            raise NotFoundException("ApprovalTask", task_id)

        manifest = db.query(ArtifactManifest).filter(ArtifactManifest.id == task.artifact_manifest_id).first()

        # Critical Safety Gate Revalidation: Hash matching check
        if artifact_hash != manifest.content_hash:
            raise ArtifactHashMismatchException(
                f"Provided hash '{artifact_hash}' does not match locked artifact hash '{manifest.content_hash}'."
            )

        if decision == "APPROVE":
            if not attestation or len(attestation.strip()) == 0:
                raise DomainException(
                    status_code=422,
                    code="ATTESTATION_REQUIRED",
                    message="Attestation statement is required for approval.",
                )
            if not mfa_verified:
                raise DomainException(
                    status_code=422,
                    code="MFA_REQUIRED",
                    message="MFA verification is mandatory to approve trade executions.",
                )
        elif decision in ("REJECT", "MODIFY"):
            if not reason or len(reason.strip()) == 0:
                raise DomainException(
                    status_code=422,
                    code="REASON_REQUIRED",
                    message=f"Reason explanation is required for decision '{decision}'.",
                )

        approval_decision = ApprovalDecision(
            tenant_id=task.tenant_id,
            approval_task_id=task.id,
            decided_by=decided_by,
            artifact_hash=artifact_hash,
            decision=decision,
            reason=reason,
            attestation=attestation,
            mfa_verified=mfa_verified,
            decided_at=datetime.now(timezone.utc),
        )
        db.add(approval_decision)
        db.flush()

        workflow = db.query(Workflow).filter(Workflow.id == task.workflow_id).first()

        if decision == "APPROVE":
            task.status = "APPROVED"
            WorkflowService.transition_stage(
                db=db,
                workflow=workflow,
                actor_id=decided_by,
                to_stage="TRADE_EXECUTION",
                to_status="APPROVED",
                reason=f"Human Approval granted by user {decided_by}. Attestation: '{attestation}'",
            )
        elif decision == "REJECT":
            task.status = "REJECTED"
            workflow.status = "REJECTED"
        elif decision == "MODIFY":
            task.status = "REJECTED"
            # Modify routes back to Strategy stage to generate updated draft
            workflow.stage = "PORTFOLIO_STRATEGY"
            workflow.status = "DRAFT"

        AuditService.record_audit_event(
            db=db,
            tenant_id=task.tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="USER",
            actor_id=decided_by,
            action=f"approval.decision_{decision.lower()}",
            resource_type="approval_decision",
            resource_id=approval_decision.id,
            outcome="SUCCESS",
            payload={
                "decision": decision,
                "task_id": str(task.id),
                "artifact_hash": artifact_hash,
                "attestation": attestation,
            },
        )

        db.commit()
        db.refresh(approval_decision)
        return approval_decision
