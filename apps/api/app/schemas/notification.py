from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict


class NotificationRead(BaseModel):
    id: UUID
    tenant_id: UUID
    recipient_id: UUID
    title: str
    message: str
    category: str
    link_url: str | None = None
    is_read: bool = False
    created_at: datetime = datetime.now()

    model_config = ConfigDict(from_attributes=True)
