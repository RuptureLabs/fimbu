from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable
from fimbu.core.types import T


if TYPE_CHECKING:
    from uuid import UUID
    

__all__ = ["RoleProtocol", "UserProtocol", "UserRoleProtocol", "RoleT", "UserT", "UserRoleT"]



@runtime_checkable
class RoleProtocol(Protocol[T]):
    """The base role type."""

    id: UUID
    name: str
    description: str


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
class UserRoleProtocol(Protocol):
    """The base SQLAlchemy user type."""

    role: RoleProtocol
    user: UserProtocol
    assigned_at: datetime


RoleT = TypeVar("RoleT", bound="RoleProtocol")
UserT = TypeVar("UserT", bound="UserProtocol")
UserRoleT = TypeVar("UserRoleT", bound="UserRoleProtocol")
