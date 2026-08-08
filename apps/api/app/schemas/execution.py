from datetime import datetime
from decimal import Decimal
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class ExecutionIntentCreateRequest(BaseModel):
    approved_artifact_id: UUID
    approved_artifact_hash: str = Field(..., min_length=64, max_length=64)
    account_id: UUID
    integration_id: UUID
    idempotency_key: str = Field(..., min_length=8, max_length=120)


class FillRead(BaseModel):
    id: UUID
    broker_order_id: UUID
    execution_id: str
    quantity: Decimal
    price: Decimal
    venue: str
    executed_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrokerOrderEventRead(BaseModel):
    id: UUID
    broker_order_id: UUID
    provider_message_id: str
    sequence_number: int
    event_type: str
    payload: dict[str, Any]
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)


class BrokerOrderRead(BaseModel):
    id: UUID
    execution_intent_id: UUID
    instrument_id: UUID
    client_order_id: str
    provider_order_id: str | None
    side: str
    order_type: str
    quantity: Decimal
    limit_price: Decimal | None
    status: str
    created_at: datetime
    events: list[BrokerOrderEventRead] = []
    fills: list[FillRead] = []

    model_config = ConfigDict(from_attributes=True)


class ExecutionIntentRead(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_id: UUID
    approval_decision_id: UUID
    artifact_manifest_id: UUID
    artifact_hash: str
    account_id: UUID
    integration_id: UUID
    idempotency_key: str
    status: str
    created_at: datetime
    orders: list[BrokerOrderRead] = []

    model_config = ConfigDict(from_attributes=True)
