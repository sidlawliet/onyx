from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import ExecutionIntent, Tenant, User
from apps.api.app.schemas.execution import ExecutionIntentCreateRequest, ExecutionIntentRead
from apps.api.app.services.execution_service import ExecutionService

router = APIRouter()


@router.post("", response_model=ExecutionIntentRead, status_code=201)
def submit_execution_intent(
    request: ExecutionIntentCreateRequest,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Submit trade execution strictly for a pre-approved recommendation artifact manifest."""
    return ExecutionService.execute_approved_intent(
        db=db,
        tenant_id=tenant.id,
        actor_id=user.id,
        approved_artifact_id=request.approved_artifact_id,
        approved_artifact_hash=request.approved_artifact_hash,
        account_id=request.account_id,
        integration_id=request.integration_id,
        idempotency_key=request.idempotency_key,
    )


@router.get("", response_model=list[ExecutionIntentRead])
def list_execution_intents(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """List execution intents and order statuses for the active tenant."""
    return db.query(ExecutionIntent).filter(ExecutionIntent.tenant_id == tenant.id).order_by(ExecutionIntent.created_at.desc()).all()


@router.get("/{intent_id}", response_model=ExecutionIntentRead)
def get_execution_intent(
    intent_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get execution intent details, broker orders, and fills by ID."""
    intent = db.query(ExecutionIntent).filter(ExecutionIntent.id == intent_id, ExecutionIntent.tenant_id == tenant.id).first()
    if not intent:
        raise NotFoundException("ExecutionIntent", intent_id)
    return intent
