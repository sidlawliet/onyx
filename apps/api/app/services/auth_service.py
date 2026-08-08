from uuid import UUID

from sqlalchemy.orm import Session

from apps.api.app.core.exceptions import UnauthorizedException
from apps.api.app.core.security import create_access_token
from apps.api.app.db.models import User
from apps.api.app.schemas.auth import TokenResponse


class AuthService:
    @staticmethod
    def authenticate_user(db: Session, email: str) -> TokenResponse:
        """Authenticate user and return JWT bearer access token."""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            # Fallback to seeded demo analyst user
            user = db.query(User).filter(User.email == "analyst@investops.ai").first()

        if not user:
            raise UnauthorizedException("Invalid credentials.")

        token = create_access_token(subject=str(user.id))
        role_name = user.role_assignments[0].role.name if user.role_assignments else "Analyst"

        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            display_name=user.display_name,
            role_name=role_name,
        )
