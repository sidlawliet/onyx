from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class AuditEventRead(BaseModel):
    id: UUID
    tenant_id: UUID
    workflow_id: UUID | None
    trace_id: UUID
    actor_type: str
    actor_id: UUID
    action: str
    resource_type: str
    resource_id: UUID | None
    outcome: str
    payload: dict[str, Any]
    previous_event_hash: str | None
    event_hash: str
    occurred_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuditExportRequest(BaseModel):
    trace_id: UUID | None = None
    workflow_id: UUID | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None


class AuditExportRead(BaseModel):
    export_id: UUID
    total_events: int
    chain_valid: bool
    manifest_hash: str
    events: list[AuditEventRead]
