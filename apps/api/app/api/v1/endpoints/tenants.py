from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.db.models import Tenant, User
from apps.api.app.schemas.tenant import TenantRead, UserRead
from apps.api.app.services.tenant_service import TenantService

router = APIRouter()


@router.get("", response_model=list[TenantRead])
def list_tenants(db: Session = Depends(get_db)):
    """List tenant workspaces."""
    return TenantService.list_tenants(db)


@router.get("/current", response_model=TenantRead)
def get_current_tenant_details(tenant: Tenant = Depends(get_current_tenant)):
    """Get active tenant workspace details."""
    return tenant


@router.get("/users", response_model=list[UserRead])
def list_tenant_users(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """List users belonging to the active tenant workspace."""
    return TenantService.list_users(db, tenant.id)
