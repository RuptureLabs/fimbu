"""User Routes."""
from __future__ import annotations

from uuid import UUID

from litestar import Controller, get, put, post, delete
from litestar.di import Provide
from litestar.params import Parameter
from litestar.repository.exceptions import ConflictError

from fimbu.conf import settings
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.guards import requires_superuser
from fimbu.contrib.auth.service import UserService, UserServiceType
from fimbu.contrib.auth.utils import get_path
from fimbu.contrib.auth.schemas import PermissionScope
from fimbu.contrib.auth.dto import PermissionScopeUpdateDTO
from fimbu.contrib.schema import Message



PREFIX: str = settings.AUTH_PREFIX


class PermissionController(Controller):
    """Handles the adding and removing of User permissions."""

    tags = ["Auth - Permissions"]
    guards = [requires_superuser]
    dependencies = {
        "service": Provide(provide_user_service),
    }
    signature_namespace = {"BaseUserService": UserService}

    @get(
        operation_id="GetScopes",
        name="scopes:get",
        path=get_path("/scopes/", PREFIX)
    )
    async def get_scopes(self, service: UserServiceType) -> list[PermissionScope]:
        """Get all scopes."""
        scopes = await service.get_all_scopes()
        return service.to_schema(scopes)
    

    @get(
        operation_id="GetUserScopes",
        name="user_scopes:get",
        path=get_path("/scopes/users", PREFIX)
    )
    async def get_user_scopes(self, user_id: UUID, service: UserServiceType) -> list[PermissionScope]:
        """Get all user's scopes."""
        scopes = await service.get_user_scopes(user_id)
        return service.to_schema(scopes)
    

    @put(
        operation_id="UpdateScopes",
        name="scopes:update",
        path=get_path("/scopes", PREFIX),
        dto=PermissionScopeUpdateDTO,
    )
    async def update_scopes(
        self,
        data: PermissionScope,
        service: UserServiceType,
    ) -> Message:
        """Update user's scopes."""
        return Message(detail="Scopes updated")
    

    @post(
        operation_id="SuscribeToScope",
        name="scopes:suscribe",
        path=get_path("/scopes/suscribe", PREFIX),
    )
    async def suscribe_to_scope(
        self,
        user_id: UUID,
        scope_slug: str,
        service: UserServiceType,
    ) -> Message:
        """Suscribe a user to a scope."""
        return Message(detail="User suscribed to scope")


    @delete(
        operation_id="RevokeScope",
        name="scopes:revoke",
        path=get_path("/scopes/revoke", PREFIX),
    )
    async def revoke_scope(
        self,
        user_id: UUID,
        scope_slug: str,
        service: UserServiceType,
    ) -> None:
        """Revoke a user from a scope."""
        return None