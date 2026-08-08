from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class IntegrationRead(BaseModel):
    id: UUID
    tenant_id: UUID
    name: str
    category: str
    environment: str
    provider: str
    status: str
    config: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class AgentStatusRead(BaseModel):
    agent_id: str
    name: str
    stage: str
    status: str  # IDLE, RUNNING, COMPLETED, ERROR
    last_execution_at: datetime | None = None


class SystemHealthRead(BaseModel):
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    environment: str
    database_connected: bool
    active_workflows_count: int
    pending_approvals_count: int
    agents: list[AgentStatusRead] = []
