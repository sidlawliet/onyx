from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.core.dependencies import get_current_user, get_db
from apps.api.app.db.models import User
from apps.api.app.schemas.auth import LoginRequest, TokenResponse, UserContext
from apps.api.app.services.auth_service import AuthService

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user credentials and return bearer JWT token."""
    return AuthService.authenticate_user(db, email=request.email)


@router.get("/me", response_model=UserContext)
def get_current_user_profile(user: User = Depends(get_current_user)):
    """Get active authenticated user context."""
    return UserContext(
        id=user.id,
        tenant_id=user.tenant_id,
        email=user.email,
        display_name=user.display_name,
        mfa_enabled=user.mfa_enabled,
        status=user.status,
    )
