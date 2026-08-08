from datetime import datetime
from typing import Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class TenantRead(BaseModel):
    id: UUID
    slug: str
    name: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RoleRead(BaseModel):
    id: UUID
    name: str
    permissions: dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: UUID
    tenant_id: UUID
    email: str
    display_name: str
    status: str
    mfa_enabled: bool
    is_service_principal: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
