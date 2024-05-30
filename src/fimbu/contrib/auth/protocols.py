from __future__ import annotations

from typing import TYPE_CHECKING, Any, Protocol, TypeVar, runtime_checkable
from fimbu.core.types import T


if TYPE_CHECKING:
    from uuid import UUID
    

__all__ = ["RoleProtocol", "UserProtocol", "RoleT", "UserT"]



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
    roles: list[RoleProtocol]

    def __init__(*args: Any, **kwargs: Any) -> None:
        ...


RoleT = TypeVar("RoleT", bound="RoleProtocol")
UserT = TypeVar("UserT", bound="UserProtocol")
