from __future__ import annotations

from typing import Annotated

from datetime import datetime  # noqa: TCH003
from uuid import UUID  # noqa: TCH003
from dataclasses import dataclass

import msgspec
from msgspec import Meta

from fimbu.contrib.auth.protocols import UserT
from fimbu.contrib.schema import BaseStruct

__all__ = (
    "AccountLogin",
    "AccountRegister",
    "User",
)

class AccountLogin(BaseStruct):
    email: str
    password: str


class AccountRegister(BaseStruct):
    email: str
    password: str
    username: str | None = None


class User(BaseStruct):
    """User properties to use for a response."""
    id: UUID
    email: str
    username: str | None = None
    is_superuser: bool = False
    is_active: bool = False
    is_verified: bool = False
    verified_at: datetime | None = None
    joined_at: datetime | None = None


class PermissionScope(BaseStruct, kw_only=True):
    name: str
    slug: str
    codename: str
    default: bool
    default_permissins: str
    description: str


class Permission(BaseStruct, omit_defaults=True):
    id : UUID
    assigned_at: datetime
    scope: PermissionScope
    can_read: bool
    can_write: bool
    can_update: bool
    can_delete: bool
    can_approve: bool


class PermissionUpdate(BaseStruct, omit_defaults=True):
    scope: str
    can_read: bool | None | msgspec.UnsetType = msgspec.UNSET
    can_write: bool | None | msgspec.UnsetType = msgspec.UNSET
    can_update: bool | None | msgspec.UnsetType = msgspec.UNSET
    can_delete: bool | None | msgspec.UnsetType = msgspec.UNSET
    can_approve: bool | None | msgspec.UnsetType = msgspec.UNSET


@dataclass
class RuntimeUser:
    base : UserT
    permissions: dict[str, PermissionUpdate]
