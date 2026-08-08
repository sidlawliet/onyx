from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import ApprovalTask, Tenant, User
from apps.api.app.schemas.approval import ApprovalDecisionRequest, ApprovalDecisionRead, ApprovalTaskRead
from apps.api.app.services.approval_service import ApprovalService

router = APIRouter()


@router.post("/recommendation-versions/{recommendation_version_id}/submit", response_model=ApprovalTaskRead)
def submit_for_approval(
    recommendation_version_id: UUID,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Submit a validated recommendation to the Human Approval Gate with locked artifact manifest."""
    return ApprovalService.submit_for_approval(
        db=db, recommendation_version_id=recommendation_version_id, actor_id=user.id
    )


@router.post("/tasks/{task_id}/decision", response_model=ApprovalDecisionRead)
def record_approval_decision(
    task_id: UUID,
    request: ApprovalDecisionRequest,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Record explicit human approval decision (APPROVE, REJECT, or MODIFY) with attestation and MFA verification."""
    return ApprovalService.record_decision(
        db=db,
        task_id=task_id,
        decided_by=user.id,
        decision=request.decision,
        artifact_hash=request.artifact_hash,
        attestation=request.attestation,
        reason=request.reason,
        mfa_verified=request.mfa_verified,
    )


@router.get("/tasks", response_model=list[ApprovalTaskRead])
def list_approval_tasks(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """List pending and historical approval tasks for the active tenant."""
    return db.query(ApprovalTask).filter(ApprovalTask.tenant_id == tenant.id).order_by(ApprovalTask.created_at.desc()).all()


@router.get("/tasks/{task_id}", response_model=ApprovalTaskRead)
def get_approval_task(
    task_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get approval task details by ID."""
    task = db.query(ApprovalTask).filter(ApprovalTask.id == task_id, ApprovalTask.tenant_id == tenant.id).first()
    if not task:
        raise NotFoundException("ApprovalTask", task_id)
    return task
