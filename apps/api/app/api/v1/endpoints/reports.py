from typing import Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_db
from apps.api.app.db.models import ResearchReport, Tenant

router = APIRouter()


@router.get("", response_model=list[dict[str, Any]])
def list_reports(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """List all generated institutional research and strategy reports."""
    reports = db.query(ResearchReport).filter(ResearchReport.tenant_id == tenant.id).all()
    return [
        {
            "id": str(r.id),
            "title": r.title,
            "status": r.status,
            "created_at": r.created_at,
            "version_count": len(r.versions),
        }
        for r in reports
    ]
