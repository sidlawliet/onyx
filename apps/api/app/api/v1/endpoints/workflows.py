from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import Tenant, User, Workflow
from apps.api.app.schemas.workflow import WorkflowCreateRequest, WorkflowRead
from apps.api.app.services.workflow_service import WorkflowService

router = APIRouter()


@router.post("", response_model=WorkflowRead, status_code=201)
def create_workflow(
    request: WorkflowCreateRequest,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Create a new 5-stage institutional workflow starting at MARKET_INTELLIGENCE."""
    return WorkflowService.create_workflow(
        db=db,
        tenant_id=tenant.id,
        user_id=user.id,
        portfolio_id=request.portfolio_id,
        title=request.title,
    )


@router.get("", response_model=list[WorkflowRead])
def list_workflows(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """List workflows for active tenant."""
    return db.query(Workflow).filter(Workflow.tenant_id == tenant.id).order_by(Workflow.created_at.desc()).all()


@router.get("/{workflow_id}", response_model=WorkflowRead)
def get_workflow(
    workflow_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get workflow details and transition history by ID."""
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.tenant_id == tenant.id)
        .first()
    )
    if not workflow:
        raise NotFoundException("Workflow", workflow_id)
    return workflow
