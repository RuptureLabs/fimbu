from uuid import UUID
from pydantic import BaseModel, EmailStr

__all__ = [
    "ForgotPasswordSchema",
    "ResetPasswordSchema",
    "AuthenticationSchema",
    "UserRoleSchema",
]


class AuthenticationSchema(BaseModel):
    """User authentication schema."""

    email: EmailStr
    password: str


class ForgotPasswordSchema(BaseModel):
    """Forgot password schema."""
    email: EmailStr


class UserRegistrationSchema(BaseModel):
    """User registration schema"""
    email : EmailStr
    first_name: str
    user_name: str
    last_name: str
    avatar_url: str
    password : str


class UserSchema(BaseModel):
    """User schema."""
    id: UUID | None = None
    email: str | None = None
    password_hash: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    avatar_url: str | None = None


class ResetPasswordSchema(BaseModel):
    """Reset password schema."""

    token: str
    password: str


class RoleSchema(BaseModel):
    id: UUID
    name: str
    description: str


class UserRoleSchema(BaseModel):
    """User role association schema."""

    user_id: UUID
    role_id: UUID
