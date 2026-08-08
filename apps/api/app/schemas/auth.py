from uuid import UUID
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = "demo-password"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: UUID
    email: str
    display_name: str
    role_name: str


class UserContext(BaseModel):
    id: UUID
    tenant_id: UUID
    email: str
    display_name: str
    mfa_enabled: bool
    status: str
