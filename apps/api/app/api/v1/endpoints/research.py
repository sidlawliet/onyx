from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import ResearchReport, Tenant, User
from apps.api.app.schemas.research import ResearchReportRead
from apps.api.app.services.research_service import ResearchService

router = APIRouter()


@router.post("/workflows/{workflow_id}/run", response_model=ResearchReportRead)
def run_market_intelligence(
    workflow_id: UUID,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Execute Market Intelligence Agent to generate a sourced Market Research Report for a workflow."""
    return ResearchService.run_market_intelligence(db=db, workflow_id=workflow_id, actor_id=user.id)


@router.get("/reports/{report_id}", response_model=ResearchReportRead)
def get_research_report(
    report_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Get Research Report details with versions, claims, and SEC citations."""
    report = (
        db.query(ResearchReport)
        .filter(ResearchReport.id == report_id, ResearchReport.tenant_id == tenant.id)
        .first()
    )
    if not report:
        raise NotFoundException("ResearchReport", report_id)
    return report
