import uuid
from uuid import UUID
from datetime import datetime
from fimbu.db import fields, Model, GUIDField

class UUIDMixin(Model):
    """
    UUID mixin base
    """
    id: UUID = GUIDField(primary_key=True, default=uuid.uuid4)
    """uuid primary key"""

    class Meta:
        abstract = True


class AuditMixin(Model):
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

    class Meta:
        abstract = True


class UserMixin(UUIDMixin):
    """Base fimbu user mixin."""
    email: str = fields.EmailField(max_length=255, null=False, unique=True)
    """User email"""
    password_hash: str = fields.CharField(max_length=255)
    """User password hash column"""
    is_active: bool = fields.BooleanField(default=False)
    """User active state"""
    is_verified: bool = fields.BooleanField(default=False)
    """User verified state"""
    avatar_url: str = fields.URLField(max_length=500, null=True, default=None)
    """User avatar url"""
    is_superuser: bool = fields.BooleanField(default=False)
    """User superuser indicator"""
    verified_at: datetime  = fields.DateTimeField(default=None, null=True)
    """User email verified indicator"""
    joined_at: datetime = fields.DateTimeField(auto_now=True)
    """Account created date"""


    class Meta:
        abstract = True
