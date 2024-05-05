from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Collection
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.contrib.auth.adapters.protocols import RoleT, UserT
from fimbu.db.repository import Repository


__all__ = ["RoleRepository", "UserRepository"]


class UserRepository(Repository[UserT], Generic[UserT]):
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
    
    def filter_collection_by_kwargs(self, collection: Collection[UserT], /, **kwargs: Any) -> Collection[UserT]:
        return super().filter_collection_by_kwargs(collection, **kwargs)


class RoleRepository(Repository[RoleT], Generic[RoleT, UserT]):
    """Implementation of role persistence layer."""

    def __init__(self, model_type: type[RoleT]) -> None:
        """Repository for users.

        Args:
            model_type: A subclass of `SQLAlchemyRoleModel`.
        """
        self.model_type = model_type
        super().__init__(self.model_type)

    def filter_collection_by_kwargs(self, collection: Collection[UserT], /, **kwargs: Any) -> Collection[UserT]:
        return super().filter_collection_by_kwargs(collection, **kwargs)


    async def assign_role(self, user: UserT, role: RoleT) -> UserT:
        """Add a role to a user.

        Args:
            user: The user to receive the role.
            role: The role to add to the user.
        """
        if not hasattr(user, "roles"):
            raise ImproperlyConfigured("User.roles is not set")
        user.roles.append(role)
        return user

    async def revoke_role(self, user: UserT, role: RoleT) -> UserT:
        """Revoke a role from a user.

        Args:
            user: The user to revoke the role from.
            role: The role to revoke from the user.
        """
        if not hasattr(user, "roles"):
            raise ImproperlyConfigured("User.roles is not set")
        user.roles.remove(role)
        return user
