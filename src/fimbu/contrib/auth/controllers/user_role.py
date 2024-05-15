"""User Routes."""
from __future__ import annotations

from litestar import Controller, post
from litestar.di import Provide
from litestar.params import Parameter
from litestar.repository.exceptions import ConflictError

from fimbu.conf import settings
from fimbu.contrib.auth import schemas
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.guards import requires_superuser
from fimbu.contrib.auth.service import UserService
from fimbu.contrib.auth.utils import get_path
from fimbu.contrib.schema import Message



PREFIX: str = settings.AUTH_PREFIX


class UserRoleController(Controller):
    """Handles the adding and removing of User Role records."""

    tags = ["Auth - User Roles"]
    guards = [requires_superuser]
    dependencies = {
        "users_service": Provide(provide_user_service),
    }
    signature_namespace = {"BaseUserService": UserService}

    @post(
        operation_id="AssignUserRole",
        name="users:assign-role",
        path=get_path('/roles/{role_slug:str}/assign', PREFIX),
    )
    async def assign_role(
        self,
        users_service: UserService,
        data: schemas.UserRoleAdd,
        role_slug: str = Parameter(
            title="Role Slug",
            description="The role to grant.",
        ),
    ) -> Message:
        """Create a new migration role."""
        role_id = (await users_service.get_one(slug=role_slug)).id
        user_obj = await users_service.get_one(email=data.user_name)
        if all(user_role.role_id != role_id for user_role in user_obj.roles):
            obj, created = await users_service.get_or_upsert(role_id=role_id, user_id=user_obj.id)
        if created:
            return Message(message=f"Successfully assigned the '{obj.role_slug}' role to {obj.user_email}.")
        return Message(message=f"User {obj.user_email} already has the '{obj.role_slug}' role.")

    @post(
        operation_id="RevokeUserRole",
        name="users:revoke-role",
        summary="Remove Role",
        description="Removes an assigned role from a user.",
        path=get_path('/roles/{role_slug:str}/revoke', PREFIX),
    )
    async def revoke_role(
        self,
        users_service: UserService,
        data: schemas.UserRoleRevoke,
        role_slug: str = Parameter(
            title="Role Slug",
            description="The role to revoke.",
        ),
    ) -> Message:
        """Delete a role from the system."""
        user_obj = await users_service.get_user(email=data.user_name)
        await users_service.revoke_role(user_obj, role_slug)
        return Message(message=f"Removed the '{role_slug}' role from User {user_obj.email}.")
