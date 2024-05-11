from __future__ import annotations

from datetime import datetime  # noqa: TCH003
from uuid import UUID  # noqa: TCH003

import msgspec

from fimbu.contrib.base import BaseStruct

__all__ = (
    "AccountLogin",
    "AccountRegister",
    "UserRoleAdd",
    "UserRoleRevoke",
    "UserCreate",
    "User",
    "UserRole",
    "UserTeam",
    "UserUpdate",
)




class UserRole(BaseStruct):
    """Holds role details for a user.

    This is nested in the User Model for 'roles'
    """

    role_id: UUID
    role_slug: str
    role_name: str
    assigned_at: datetime


class OauthAccount(BaseStruct):
    """Holds linked Oauth details for a user."""

    id: UUID
    oauth_name: str
    access_token: str
    account_id: str
    account_email: str
    expires_at: int | None = None
    refresh_token: str | None = None


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


class UserCreate(BaseStruct):
    email: str
    password: str
    username: str | None = None
    is_superuser: bool = False
    is_active: bool = True
    is_verified: bool = False


class UserUpdate(BaseStruct, omit_defaults=True):
    email: str | None | msgspec.UnsetType = msgspec.UNSET
    password: str | None | msgspec.UnsetType = msgspec.UNSET
    username: str | None | msgspec.UnsetType = msgspec.UNSET
    is_superuser: bool | None | msgspec.UnsetType = msgspec.UNSET
    is_active: bool | None | msgspec.UnsetType = msgspec.UNSET
    is_verified: bool | None | msgspec.UnsetType = msgspec.UNSET


class AccountLogin(BaseStruct):
    email: str
    password: str


class AccountRegister(BaseStruct):
    email: str
    password: str
    username: str | None = None


class UserRoleAdd(BaseStruct):
    """User role add ."""

    email: str


class UserRoleRevoke(BaseStruct):
    """User role revoke ."""

    email: str
