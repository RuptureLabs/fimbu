from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable
from fimbu.core.types import T


if TYPE_CHECKING:
    from uuid import UUID
    

__all__ = [
    "UserProtocol",
    "PermissionScopeProtocol",
    "PermissionProtocol",
    "UserT",
    "PermScopteT",
    "PermT",
]


@runtime_checkable
class UserProtocol(Protocol[T]):
    """The base user type."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    is_verified: bool

    def __init__(*args: Any, **kwargs: Any) -> None:
        ...


@runtime_checkable
class PermissionScopeProtocol(Protocol[T]):
    """The Permission Scope type."""

    name: str
    slug: str
    default: bool
    default_permissins: str
    description: str

    def suscribe_user(self, user: UserT) -> T:
        ...

    def unscribe_user(self, user: UserT) -> T | None:
        ...


class PermissionProtocol(Protocol[T]):
    """Permission Type"""

    user: UserT
    scope: PermScopteT
    assigned_at: datetime
    can_read: bool
    can_write: bool
    can_update: bool
    can_delete: bool
    can_approve: bool


PermScopteT = TypeVar("PermScopteT", bound="PermissionScopeProtocol")
UserT = TypeVar("UserT", bound="UserProtocol")
PermT = TypeVar("PermT", bound="PermissionProtocol")
