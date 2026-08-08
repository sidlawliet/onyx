from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import Alert, HoldingSnapshot, Tenant, User
from apps.api.app.schemas.monitoring import AlertDispositionRequest, AlertRead, HoldingSnapshotRead
from apps.api.app.schemas.workflow import WorkflowRead
from apps.api.app.services.monitoring_service import MonitoringService

router = APIRouter()


@router.post("/portfolios/{portfolio_id}/capture-snapshots", response_model=list[HoldingSnapshotRead])
def capture_holding_snapshots(
    portfolio_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Capture current portfolio holding snapshots, update market prices, and record risk/drift alerts."""
    return MonitoringService.capture_holding_snapshots(db=db, tenant_id=tenant.id, portfolio_id=portfolio_id)


@router.get("/portfolios/{portfolio_id}/holdings", response_model=list[HoldingSnapshotRead])
def list_portfolio_holdings(
    portfolio_id: UUID,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """List current holding snapshots for a portfolio."""
    return (
        db.query(HoldingSnapshot)
        .filter(HoldingSnapshot.portfolio_id == portfolio_id, HoldingSnapshot.tenant_id == tenant.id)
        .order_by(HoldingSnapshot.observed_at.desc())
        .all()
    )


@router.get("/alerts", response_model=list[AlertRead])
def list_alerts(
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """List risk and drift alerts for active tenant."""
    return db.query(Alert).filter(Alert.tenant_id == tenant.id).order_by(Alert.created_at.desc()).all()


@router.post("/alerts/{alert_id}/disposition", response_model=AlertRead)
def disposition_alert(
    alert_id: UUID,
    request: AlertDispositionRequest,
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Acknowledge or resolve a portfolio monitoring alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id, Alert.tenant_id == tenant.id).first()
    if not alert:
        raise NotFoundException("Alert", alert_id)
    alert.status = request.status
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/portfolios/{portfolio_id}/rebalance", response_model=WorkflowRead)
def trigger_rebalance_workflow(
    portfolio_id: UUID,
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """Initiate a rebalance workflow returning to the PORTFOLIO_STRATEGY stage."""
    return MonitoringService.trigger_rebalance_workflow(
        db=db, tenant_id=tenant.id, user_id=user.id, portfolio_id=portfolio_id
    )
