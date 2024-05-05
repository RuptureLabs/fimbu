from __future__ import annotations

from typing import TypeVar

from fimbu.db import Model, fields

__all__ = [
    "BaseUserMixin",
    "BaseRoleMixin",
    "UserModelType",
    "RoleModelType",
]


class BaseUserMixin(Model):
    """Base fimbu user mixin."""

    email = fields.EmailField(max_length=255, nullable=False, unique=True)
    password_hash = fields.CharField(max_length=1024)
    is_active = fields.BooleanField(nullable=False, default=False)
    is_verified = fields.BooleanField(nullable=False, default=False)

    class Meta:
        abstract = True
    

class BaseRoleMixin(Model):
    """Base fimbu role mixin."""

    name = fields.CharField(max_length=255, nullable=False, unique=True)
    description = fields.CharField(max_length=255, nullable=True)


UserModelType = TypeVar("UserModelType", bound=BaseUserMixin)
RoleModelType = TypeVar("RoleModelType", bound=BaseRoleMixin)