from __future__ import annotations

from typing import Any, Generic
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.contrib.auth.models import Role
from fimbu.contrib.auth.protocols import RoleT, UserT
from fimbu.db.repository import AsyncRepository


__all__ = ["RoleRepository", "UserRepository"]



class UserRepository(AsyncRepository[UserT], Generic[UserT]):
    """Implementation of user persistence layer."""

    def __init__(self, model_type: type[UserT]) -> None:
        """Repository for users.

        Args:
            model_type: A subclass of `UserModel`.
        """
        self.model_type = model_type
        super().__init__(self.model_type)


    async def _update(self, user: UserT, data: dict[str, Any]) -> UserT:
        for key, value in data.items():
            setattr(user, key, value)

        return user
    

    async def assign_role(self, user: UserT, role: RoleT) -> UserT:
        """Add a role to a user.

        Args:
            user: The user to receive the role.
            role: The role to add to the user.
        """
        user.roles.add(role)
        return user

    async def revoke_role(self, user: UserT, role: RoleT) -> UserT:
        """Revoke a role from a user.

        Args:
            user: The user to revoke the role from.
            role: The role to revoke from the user.
        """
        user.roles.remove(role)
        return user


class RoleRepository(AsyncRepository[Role]):
    """Role Repository."""

    model_type = Role
    