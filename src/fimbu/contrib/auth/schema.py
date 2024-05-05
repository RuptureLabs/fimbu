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
    password : str


class UserSchema(BaseModel):
    """User schema."""
    id: UUID
    email: str
    password_hash: str
    is_active: bool
    is_verified: bool


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
