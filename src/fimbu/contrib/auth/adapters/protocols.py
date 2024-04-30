from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable

if TYPE_CHECKING:
    from uuid import UUID

__all__ = ["RoleProtocol", "UserProtocol"]


@runtime_checkable
class RoleProtocol(Protocol):
    """The base role type."""

    id: UUID
    name: str
    description: str


@runtime_checkable
class UserProtocol(Protocol):
    """The base user type."""

    id: UUID
    email: str
    password_hash: str
    is_active: bool
    is_verified: bool

    def __init__(*args: Any, **kwargs: Any) -> None:
        ...


@runtime_checkable
class UserRoleProtocol(UserProtocol, Protocol):
    """The base SQLAlchemy user type."""

    roles: list[RoleProtocol]


RoleT = TypeVar("RoleT", bound="RoleProtocol")
UserT = TypeVar("UserT", bound="UserProtocol | UserRoleProtocol")
