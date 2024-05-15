"""User Account Controllers."""

from __future__ import annotations

from typing import Annotated

from litestar import Controller, delete, get, patch, post
from litestar.di import Provide
from litestar.params import Dependency, Parameter
from uuid import UUID

from fimbu.conf import settings
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.protocols import UserProtocol
from fimbu.contrib.auth.guards import requires_superuser
from fimbu.contrib.auth.schemas import User, UserCreate, UserUpdate
from fimbu.contrib.auth.service import UserServiceType
from fimbu.contrib.auth.utils import get_path
from fimbu.db.filters import FilterTypes, OffsetPagination



PREFIX: str = settings.AUTH_PREFIX


class UserController(Controller):
    """User Account Controller."""

    tags = ["Auth - Users"]
    # guards = [requires_superuser]
    dependencies = {"users_service": Provide(provide_user_service)}
    signature_namespace = {"UserService": UserServiceType}
    dto = None
    return_dto = None

    @get(
        operation_id="ListUsers",
        name="users:list",
        summary="List Users",
        description="Retrieve the users.",
        path=get_path('/users', PREFIX),
        cache=60,
    )
    async def list_users(
        self,
        users_service: UserServiceType,
        # filters: Annotated[list[FilterTypes], Dependency(skip_validation=True)],
    ) -> OffsetPagination[User]:
        """List users."""
        results, total = await users_service.get_all_users(), 2
        return users_service.to_schema(data=results, total=total, schema_type=User)

    @get(
        operation_id="GetUser",
        name="users:get",
        path=get_path('/users/{user_id:uuid}', PREFIX),
        summary="Retrieve the details of a user.",
    )
    async def get_user(
        self,
        users_service: UserServiceType,
        user_id: Annotated[
            UUID,
            Parameter(
                title="User ID",
                description="The user to retrieve.",
            ),
        ],
    ) -> User:
        """Get a user."""
        db_obj = await users_service.get_user(user_id)
        return users_service.to_schema(db_obj, schema_type=User)

    @post(
        operation_id="CreateUser",
        name="users:create",
        summary="Create a new user.",
        cache_control=None,
        description="A user who can login and use the system.",
        path=get_path('/users', PREFIX),
    )
    async def create_user(
        self,
        users_service: UserServiceType,
        data: UserCreate,
    ) -> User:
        """Create a new user."""
        db_obj = await users_service.register(data.to_dict())
        return users_service.to_schema(db_obj, schema_type=User)

    @patch(
        operation_id="UpdateUser",
        name="users:update",
        path=get_path('/users/{user_id:uuid}', PREFIX),
    )
    async def update_user(
        self,
        data: UserUpdate,
        users_service: UserServiceType,
        user_id: UUID = Parameter(
            title="User ID",
            description="The user to update.",
        ),
    ) -> User:
        """Create a new user."""
        db_obj = await users_service.update_user(item_id=user_id, data=data.to_dict())
        return users_service.to_schema(db_obj, schema_type=User)

    @delete(
        operation_id="DeleteUser",
        name="users:delete",
        path=get_path('/users/{user_id:uuid}', PREFIX),
        summary="Remove User",
        description="Removes a user and all associated data from the system.",
    )
    async def delete_user(
        self,
        users_service: UserServiceType,
        user_id: Annotated[
            UUID,
            Parameter(
                title="User ID",
                description="The user to delete.",
            ),
        ],
    ) -> None:
        """Delete a user from the system."""
        _ = await users_service.delete_user(user_id)
