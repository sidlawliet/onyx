from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_db
from apps.api.app.db.models import Tenant
from apps.api.app.schemas.integration import IntegrationRead
from apps.api.app.services.integration_service import IntegrationService

router = APIRouter()


@router.get("", response_model=list[IntegrationRead])
def list_integrations(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """List market data, FIX broker, and system integrations."""
    return IntegrationService.list_integrations(db, tenant.id)
