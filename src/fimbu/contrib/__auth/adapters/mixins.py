from __future__ import annotations

from typing import TypeVar, TYPE_CHECKING
from uuid import UUID
from datetime import datetime
import uuid

from fimbu.db import Model, fields

__all__ = [
    "BaseUserMixin",
    "BaseRoleMixin",
    "UserModelType",
    "RoleModelType",
]

if TYPE_CHECKING:
    from datetime import date

class BaseUUIDMixin(Model):
    """Base fimbu UUID mixin."""
    id: UUID = fields.UUIDField(primary_key=True, default=uuid.uuid4)


class BaseUserMixin(BaseUUIDMixin):
    """Base fimbu user mixin."""

    email: str = fields.EmailField(max_length=255, nullable=False, unique=True)
    password_hash: str = fields.CharField(max_length=255)
    is_active: bool = fields.BooleanField(nullable=False, default=False)
    is_verified: bool = fields.BooleanField(nullable=False, default=False)
    avatar_url: str | None = fields.CharField(max_length=500, nullable=True)
    is_superuser: bool = fields.BooleanField(nullable=False, default=False)
    verified_at: date | None = fields.DateField(nullable=True, auto_now=True)
    joined_at: date = fields.DateField(default=datetime.now)


    class Meta:
        abstract = True
    

class BaseRoleMixin(Model):
    """Base fimbu role mixin."""

    name = fields.CharField(max_length=255, nullable=False, unique=True)
    description = fields.CharField(max_length=255, nullable=True)


UserModelType = TypeVar("UserModelType", bound=BaseUserMixin)
RoleModelType = TypeVar("RoleModelType", bound=BaseRoleMixin)