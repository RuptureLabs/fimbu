"""Role Routes."""
from __future__ import annotations
from typing import Any
from uuid import UUID

from litestar import Controller, Request, post, get
from litestar.di import Provide


from fimbu.conf import settings
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.guards import requires_superuser
from fimbu.contrib.auth.protocols import RoleT
from fimbu.contrib.auth.service import UserService, UserServiceType
from fimbu.contrib.auth.utils import get_path
from fimbu.contrib.auth.models import Role
from fimbu.contrib.schema import Message


PREFIX: str = settings.AUTH_PREFIX


class RoleController(Controller):
    """Handles the adding and removing of new Roles."""

    tags = ["Auth - User Roles"]
    # guards = [requires_superuser]
    dependencies = {
        "service": Provide(provide_user_service),
    }
    signature_namespace = {
        "UserService": UserService,
        "UserServiceType": UserServiceType,
    }

    @get(
        operation_id="GetRoles",
        name="roles:get",
        path=get_path("/roles/", PREFIX)
    )
    async def get_roles(self, service: UserServiceType) -> list[RoleT]:
        """Get all roles."""
        roles = await service.get_roles()
        return roles
    
    @get(
        operation_id="GetRole",
        name="role:get",
        path=get_path("/roles/{slug:str}", PREFIX)
    )
    async def get_role(self, request:Request[Any, Any, Any],  service: UserServiceType, slug: str) -> RoleT:
        """Get all roles."""
        roles = await service.get_role(slug=slug)
        return roles
    