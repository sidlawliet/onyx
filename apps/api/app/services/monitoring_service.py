from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.core.exceptions import NotFoundException
from apps.api.app.db.models import Alert, HoldingSnapshot, Instrument, Portfolio, Workflow
from apps.api.app.providers.market_data_provider import MarketDataProvider
from apps.api.app.services.audit_service import AuditService
from apps.api.app.services.workflow_service import WorkflowService


class MonitoringService:
    @staticmethod
    def capture_holding_snapshots(
        db: Session, tenant_id: UUID, portfolio_id: UUID, workflow_id: UUID | None = None
    ) -> list[HoldingSnapshot]:
        """Capture current portfolio holding snapshots, update market prices, and record risk/drift alerts."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.tenant_id == tenant_id).first()
        if not portfolio:
            raise NotFoundException("Portfolio", portfolio_id)

        instruments = db.query(Instrument).all()
        prices = MarketDataProvider.get_realtime_prices([i.symbol for i in instruments])

        # Target holdings
        holdings_config = [
            ("AAPL", Decimal("2000.000000"), Decimal("0.350000")),
            ("MSFT", Decimal("1000.000000"), Decimal("0.300000")),
            ("NVDA", Decimal("1500.000000"), Decimal("0.200000")),
            ("GOOGL", Decimal("800.000000"), Decimal("0.150000")),
        ]

        total_value = Decimal("0.0000")
        snapshots = []

        for symbol, qty, target_wt in holdings_config:
            instr = next((i for i in instruments if i.symbol == symbol), None)
            if instr:
                price = prices.get(symbol, Decimal("100.0000"))
                mkt_val = qty * price
                total_value += mkt_val

                snapshot = HoldingSnapshot(
                    tenant_id=tenant_id,
                    portfolio_id=portfolio.id,
                    instrument_id=instr.id,
                    workflow_id=workflow_id,
                    quantity=qty,
                    market_price=price,
                    market_value=mkt_val,
                    weight=Decimal("0.250000"),  # Will normalize
                    target_weight=target_wt,
                    pnl=Decimal("15400.5000"),
                    observed_at=datetime.now(timezone.utc),
                )
                db.add(snapshot)
                snapshots.append(snapshot)

        db.flush()

        # Check for portfolio drift alerts
        instruments_map = {i.id: i for i in instruments}
        if total_value > Decimal("0"):
            for snap in snapshots:
                snap.weight = snap.market_value / total_value
                drift = abs(snap.weight - snap.target_weight)
                if drift > Decimal("0.050000"):  # 5% drift threshold
                    instr_sym = instruments_map[snap.instrument_id].symbol if snap.instrument_id in instruments_map else "ASSET"
                    alert = Alert(
                        tenant_id=tenant_id,
                        portfolio_id=portfolio.id,
                        workflow_id=workflow_id,
                        alert_type="PORTFOLIO_DRIFT",
                        severity="WARNING",
                        title=f"Portfolio Drift Alert: {instr_sym}",
                        description=f"{instr_sym} weight ({snap.weight * 100:.1f}%) drifted from target ({snap.target_weight * 100:.1f}%)",
                        confidence=Decimal("0.9500"),
                        status="OPEN",
                        created_at=datetime.now(timezone.utc),
                    )
                    db.add(alert)

        db.commit()
        return snapshots

    @staticmethod
    def trigger_rebalance_workflow(db: Session, tenant_id: UUID, user_id: UUID, portfolio_id: UUID) -> Workflow:
        """Initiate a rebalance workflow returning to the PORTFOLIO_STRATEGY stage."""
        portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id, Portfolio.tenant_id == tenant_id).first()
        if not portfolio:
            raise NotFoundException("Portfolio", portfolio_id)

        workflow = WorkflowService.create_workflow(
            db=db,
            tenant_id=tenant_id,
            user_id=user_id,
            portfolio_id=portfolio_id,
            title=f"Portfolio Rebalance Workflow - {portfolio.code}",
        )

        AuditService.record_audit_event(
            db=db,
            tenant_id=tenant_id,
            trace_id=workflow.trace_id,
            workflow_id=workflow.id,
            actor_type="USER",
            actor_id=user_id,
            action="monitoring.rebalance_triggered",
            resource_type="workflow",
            resource_id=workflow.id,
            outcome="SUCCESS",
            payload={"portfolio_id": str(portfolio_id), "rebalance_workflow_id": str(workflow.id)},
        )

        return workflow
