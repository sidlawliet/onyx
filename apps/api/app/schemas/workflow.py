from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field


class WorkflowCreateRequest(BaseModel):
    portfolio_id: UUID
    title: str = Field(..., min_length=3, max_length=240)


class WorkflowTransitionRead(BaseModel):
    id: UUID
    workflow_id: UUID
    actor_id: UUID
    from_stage: str | None
    to_stage: str
    from_status: str | None
    to_status: str
    reason: str | None
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkflowRead(BaseModel):
    id: UUID
    tenant_id: UUID
    portfolio_id: UUID
    created_by: UUID
    trace_id: UUID
    title: str
    stage: str
    status: str
    version: int
    created_at: datetime
    updated_at: datetime
    transitions: list[WorkflowTransitionRead] = []

    model_config = ConfigDict(from_attributes=True)
