from datetime import datetime, timezone
import uuid
from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.schemas.notification import NotificationRead


class NotificationService:
    @staticmethod
    def list_user_notifications(db: Session, tenant_id: UUID, user_id: UUID) -> list[NotificationRead]:
        """Return notifications for active user."""
        return [
            NotificationRead(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                recipient_id=user_id,
                title="Approval Required: Recommendation WF-DEMO-001",
                message="Portfolio Recommendation v1 submitted to Human Approval Gate. Attestation required.",
                category="APPROVAL_TASK",
                link_url="/approvals/task-001",
                is_read=False,
                created_at=datetime.now(timezone.utc),
            ),
            NotificationRead(
                id=uuid.uuid4(),
                tenant_id=tenant_id,
                recipient_id=user_id,
                title="Trade Execution Completed",
                message="Execution Intent completed across 4 orders ($1.5M executed).",
                category="TRADE_EXECUTION",
                link_url="/execution/intent-001",
                is_read=True,
                created_at=datetime.now(timezone.utc),
            ),
        ]
