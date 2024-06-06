from __future__ import annotations

from typing import Any, Generic
from uuid import UUID
from fimbu.contrib.auth.models import PermissionScope, Permission
from fimbu.contrib.auth.protocols import PermScopteT, PermT, UserT
from fimbu.db.repository import AsyncRepository


__all__ = ["PermissionScopeRepository", "UserRepository"]



class UserRepository(AsyncRepository[UserT], Generic[UserT]):
    """Implementation of user persistence layer."""

    def __init__(self, model_type: type[UserT]) -> None:
        """Repository for users.

        Args:
            model_type: A subclass of `UserModel`.
        """
        self.model_type = model_type
        super().__init__(self.model_type)


class PermissionScopeRepository(AsyncRepository[PermissionScope]):

    def __init__(self) -> None:
        self.model_type = PermissionScope
        super().__init__(self.model_type)

    
    async def suscribe_user(self, scope_id: UUID, user: UserT) -> PermT:
        scope = await self.get(scope_id)
        return await scope.suscribe_user(user)
    

    async def unscribe_user(self, scope_id: UUID, user: UserT) -> PermT | None:
        scope = await self.get(scope_id)
        return await scope.unscribe_user(user)



class PermissionRepository(AsyncRepository[Permission]):

    def __init__(self) -> None:
        self.model_type = Permission
        super().__init__(self.model_type)
