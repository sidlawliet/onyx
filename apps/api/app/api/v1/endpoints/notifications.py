from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_tenant, get_current_user, get_db
from apps.api.app.db.models import Tenant, User
from apps.api.app.schemas.notification import NotificationRead
from apps.api.app.services.notification_service import NotificationService

router = APIRouter()


@router.get("", response_model=list[NotificationRead])
def list_notifications(
    user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
    db: Session = Depends(get_db),
):
    """List notifications for current user."""
    return NotificationService.list_user_notifications(db=db, tenant_id=tenant.id, user_id=user.id)
