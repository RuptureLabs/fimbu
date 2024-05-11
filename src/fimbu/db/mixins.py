import uuid
from uuid import UUID
from datetime import datetime
from fimbu.db import fields

class UUIDMixin:
    """
    UUID mixin base
    """
    id: UUID = fields.UUIDField(primary_key=True, default=uuid.uuid4)
    """uuid primary key"""


class AuditMixin:
    """
    Audit columns mixin
    """
    created_at: datetime = fields.DateTimeField(auto_now=True)
    """create indicator"""
    updated_at: datetime = fields.DateTimeField(auto_now_add=True)
    """last update indicator"""
    deleted: bool = fields.BooleanField(default=False)
    """deleted indicator"""
    is_active: bool = fields.BooleanField(default=False)
    """archived indicator"""


class UserMixin(UUIDMixin):
    """Base fimbu user mixin."""
    email: str = fields.EmailField(max_length=255, nullable=False, unique=True)
    """User email"""
    password_hash: str = fields.CharField(max_length=255)
    """User password hash column"""
    is_active: bool = fields.BooleanField(nullable=False, default=False)
    """User active state"""
    is_verified: bool = fields.BooleanField(nullable=False, default=False)
    """User verified state"""
    avatar_url: str | None = fields.CharField(max_length=500, nullable=True)
    """User avatar url"""
    is_superuser: bool = fields.BooleanField(nullable=False, default=False)
    """User superuser indicator"""
    verified_at: datetime | None = fields.DateTimeField(nullable=True)
    """User email verified indicator"""
    joined_at: datetime = fields.DateTimeField(default=datetime.now)
    """Account created date"""
