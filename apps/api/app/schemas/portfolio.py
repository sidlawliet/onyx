from datetime import datetime
from decimal import Decimal
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class PortfolioRead(BaseModel):
    id: UUID
    tenant_id: UUID
    code: str
    name: str
    base_currency: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AccountRead(BaseModel):
    id: UUID
    tenant_id: UUID
    portfolio_id: UUID
    account_number: str
    broker_name: str
    available_cash: Decimal
    currency: str
    status: str

    model_config = ConfigDict(from_attributes=True)


class InstrumentRead(BaseModel):
    id: UUID
    symbol: str
    name: str
    asset_class: str
    currency: str
    exchange: str

    model_config = ConfigDict(from_attributes=True)
