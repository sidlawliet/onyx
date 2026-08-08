from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_db
from apps.api.app.db.models import Tenant
from apps.api.app.schemas.integration import SystemHealthRead
from apps.api.app.services.integration_service import IntegrationService

router = APIRouter()


@router.get("", response_model=SystemHealthRead)
def get_system_health(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """Get overall platform system health, active agent statuses, and database connectivity metrics."""
    return IntegrationService.get_system_health(db, tenant.id)
