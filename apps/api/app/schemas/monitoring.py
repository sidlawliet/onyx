from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class HoldingSnapshotRead(BaseModel):
    id: UUID
    tenant_id: UUID
    portfolio_id: UUID
    instrument_id: UUID
    workflow_id: UUID | None
    quantity: Decimal
    market_price: Decimal
    market_value: Decimal
    weight: Decimal
    target_weight: Decimal
    pnl: Decimal
    observed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertRead(BaseModel):
    id: UUID
    tenant_id: UUID
    portfolio_id: UUID
    workflow_id: UUID | None
    alert_type: str
    severity: str
    title: str
    description: str
    confidence: Decimal | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AlertDispositionRequest(BaseModel):
    status: str  # ACKNOWLEDGED, RESOLVED
    comment: str | None = None
