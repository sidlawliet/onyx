from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_db
from apps.api.app.db.models import Tenant
from apps.api.app.schemas.portfolio import AccountRead, InstrumentRead, PortfolioRead
from apps.api.app.services.tenant_service import TenantService

router = APIRouter()


@router.get("", response_model=list[PortfolioRead])
def list_portfolios(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """List institutional portfolios owned by the active tenant."""
    return TenantService.list_portfolios(db, tenant.id)


@router.get("/accounts", response_model=list[AccountRead])
def list_accounts(tenant: Tenant = Depends(get_current_tenant), db: Session = Depends(get_db)):
    """List execution accounts for the active tenant."""
    return TenantService.list_accounts(db, tenant.id)


@router.get("/instruments", response_model=list[InstrumentRead])
def list_instruments(db: Session = Depends(get_db)):
    """List tradeable instrument reference data."""
    return TenantService.list_instruments(db)
