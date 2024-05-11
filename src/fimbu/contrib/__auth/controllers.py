"""User Account Controllers."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import UUID

from litestar import Controller, Request, Response, delete, get, patch, post, put
from litestar.di import Provide
from litestar.security.session_auth import SessionAuth
from litestar.security.jwt import OAuth2Login
from litestar.contrib.jwt import JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth
from litestar.exceptions import NotAuthorizedException, PermissionDeniedException

from fimbu.core.exceptions import ImproperlyConfiguredException
from fimbu.conf import settings
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.adapters.protocols import RoleT, UserT
from fimbu.contrib.auth.service import UserServiceType
from fimbu.contrib.auth.utils import get_auth_backend, get_auth_config, get_path, get_user_model
from fimbu.contrib.auth.schema import (
    RoleSchema, UserRegistrationSchema, UserSchema,
    AuthenticationSchema, ForgotPasswordSchema, 
    ResetPasswordSchema, UserRoleSchema
)
from fimbu.utils.text import slugify


if TYPE_CHECKING:
    from typing import Any
    from litestar.contrib.pydantic import PydanticDTO
    from litestar.types import Guard
    from fimbu.contrib.auth.adapters.protocols import RoleT, UserT



IDENTIFIER_URI = settings.AUTH_UUID_IDENTIFIERS
PREFIX: str = settings.AUTH_PREFIX
TAGS: list[str] = settings.AUTH_TAGS


_auth_backend: JWTCookieAuth | JWTAuth | OAuth2PasswordBearerAuth | SessionAuth = get_auth_config("AUTH_BACKEND_CLASS")
user_read_dto: PydanticDTO = get_auth_config("USER_READ_DTO")
user_registration_dto: PydanticDTO = get_auth_config("USER_REGISTRATION_DTO")
user_update_dto: PydanticDTO = get_auth_config("USER_UPDATE_DTO")
role_create_dto: PydanticDTO = get_auth_config("ROLE_CREATE_DTO")
role_read_dto: PydanticDTO = get_auth_config("ROLE_READ_DTO")
role_update_dto: PydanticDTO = get_auth_config("ROLE_UPDATE_DTO")
guards: list[Guard] = settings.AUTH_GUARDS

LoginReturnType = cast('Any', Response[OAuth2Login] if not issubclass(_auth_backend, SessionAuth) else UserT)

UserModel = get_user_model()


class AccessController(Controller):
    """Access Controller."""

    tags = ['Access']
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)}


    @post(
        get_path("/signup", PREFIX),
        dto=user_registration_dto,
        return_dto=user_read_dto,
        exclude_from_auth=True,
        exclude_from_csrf=True,
    )
    async def register(self, data: UserRegistrationSchema, service: UserServiceType, request: Request) -> UserT:
        """Register a new user."""
        return await cast(UserT, service.register(data.model_dump(), request))
    

    @post(
        get_path("/login", PREFIX),
        return_dto=user_read_dto,
        exclude_from_auth=True,
        exclude_from_csrf=True,
    )
    async def login(self, data: AuthenticationSchema, service: UserServiceType, request: Request) -> LoginReturnType: # type: ignore
        """Authenticate a user."""
        auth_backend = get_auth_backend(request.app)

        if isinstance(auth_backend, (JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth)):
            return await self.login_jwt(data, service, request)
        elif isinstance(auth_backend, SessionAuth):
            return await self.login_session(data, service, request, auth_backend)
        else:
            raise ImproperlyConfiguredException("login can only be used with JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth or SessionAuth")
    

    async def login_jwt(self, 
        data: AuthenticationSchema,
        service: UserServiceType, 
        request: Request,
        auth_backend: JWTAuth | JWTCookieAuth | OAuth2PasswordBearerAuth | None = None) -> Response[OAuth2Login]:

        user = await service.authenticate(data, request)
        if user is None:
            raise NotAuthorizedException(detail="login failed, invalid input")

        if user.is_verified is False:
            raise PermissionDeniedException(detail="not verified")
        
        if user.is_active is False:
            raise PermissionDeniedException(detail="not active")

        return auth_backend.login(identifier=str(user.id), response_body=cast(UserT, user))
    

    async def login_session(self,
        data: AuthenticationSchema,
        service: UserServiceType, 
        request: Request,
        auth_backend: JWTAuth | JWTCookieAuth | OAuth2PasswordBearerAuth | None = None) -> UserT:
        user = await service.authenticate(data, request)
        if user is None:
            request.clear_session()
            raise NotAuthorizedException(detail="login failed, invalid input")

        request.set_session({"user_id": user.id})
        return cast(UserT, user)


    @post(
        operation_id="AccountLogout",
        name="account:logout",
        path=get_path("/logout", PREFIX),
        cache=False,
        summary="Logout",
        exclude_from_auth=True,
        exclude_from_csrf=True,
    )
    async def logout(self, request: Request) -> Response:
        """Account Logout"""
        auth_backend = get_auth_backend(request.app)
        key = None

        if isinstance(auth_backend, SessionAuth):
            request.clear_session()
        else:
            if hasattr(auth_backend, "key"):
                key = auth_backend.key
            request.cookies.pop(auth_backend.key, None)
        

        response = Response(
            {"message": "OK"},
            status_code=200,
        )

        if key:
            response.delete_cookie(auth_backend.key)
        
        return response


    @get(get_path("/profile", PREFIX), return_dto=user_read_dto)
    async def get_current_user(self, request: Request[UserT, Any, Any]) -> UserT:
        """Get current user info."""
        return request.user


    @patch(
        get_path("/profile", PREFIX),
        dto=user_update_dto,
        return_dto=user_read_dto,
    )
    async def update_current_user(self, data: UserSchema, request: Request[UserT, Any, Any], 
        service: UserServiceType) -> UserT:
        """Update the current user."""
        data.id = request.user.id
        return cast(UserT, await service.update_user(data=data))
    

    @post(
        get_path("/verify", PREFIX),
        return_dto=user_read_dto,
        exclude_from_auth=True,
    )
    async def verify(self, token: str, service: UserServiceType, request: Request) -> UserT:
        """Verify a user with a given JWT."""
        auth_backend = get_auth_backend(request.app)
        if isinstance(auth_backend, SessionAuth):
            return Response(status_code=400, content={"message": "invalid auth backend"})
        return cast(UserT, await service.verify(token, request))


class PasswordController(Controller):
    """Password Controller."""

    dependencies = {"service": Provide(provide_user_service, sync_to_thread=False)}
    tags = ["Password"]

    @post(
        get_path("/forgot-password", PREFIX),
        exclude_from_auth=True,
    )
    async def forgot_password(self, data: ForgotPasswordSchema, service: UserServiceType) -> None:
        await service.initiate_password_reset(data.email)
        return

    @post(
        get_path("/reset-password", PREFIX),
        exclude_from_auth=True,
    )
    async def reset_password(self, data: ResetPasswordSchema, service: UserServiceType) -> None:
        await service.reset_password(data.token, data.password)
        return


class UserManagementController(Controller):
    """User Management Controller."""

    dependencies = {"service": Provide(provide_user_service, sync_to_thread=False)}
    tags = ["Users"]

    @get(
        get_path(f"/users/{IDENTIFIER_URI}", PREFIX),
        dto=user_read_dto,
        return_dto=user_read_dto,
    )
    async def get_user(self, id_: UUID, service: UserServiceType) -> UserT:
        """Get a user by id."""

        return cast(UserT, await service.get_user(id_))
    

    @get(
        get_path(f"/users", PREFIX),
        dto=user_read_dto,
        return_dto=user_read_dto,
    )
    async def get_all_users(self, service: UserServiceType) -> list[UserT]:
        """Get a user by id."""

        return cast(UserT, await service.get_all_users())

    @patch(
        get_path(f"/users/{IDENTIFIER_URI}", PREFIX),
        dto=user_update_dto,
        return_dto=user_read_dto,
    )
    async def update_user(self, id_: UUID, data: UserSchema, service: UserServiceType) -> UserT:
        """Update a user's attributes."""
        data.id = id_
        return cast(UserSchema, await service.update_user(data))


    @delete(
        get_path(f"/users/{IDENTIFIER_URI}", PREFIX),
        return_dto=user_read_dto,
        status_code=200,
    )
    async def delete_user(self, id_: UUID, service: UserServiceType) -> UserT:
        """Delete a user from the database."""

        return cast(UserT, await service.delete_user(id_))


class RoleManagementController(Controller):
    """Role Management Controller."""

    dependencies = {"service": Provide(provide_user_service, sync_to_thread=False)}
    tags = ["Permission"]

    @post(
        get_path("/roles", PREFIX),
        dto=role_create_dto,
        return_dto=role_read_dto,
        guards=guards
    )
    async def create_role(self, data: RoleSchema, service: UserServiceType) -> RoleSchema:
        """Create a new role."""
        return cast(RoleT, await service.add_role(data))


    @patch(
        get_path(f"/roles/{IDENTIFIER_URI}", PREFIX),
        dto=role_update_dto,
        return_dto=role_read_dto,
        guards=guards,
    )
    async def update_role(self, id_: UUID, data: UserRoleSchema, service: UserServiceType) -> RoleT:
        """Update a role in the database."""
        data.id = id_
        return cast(RoleT, await service.update_role(id_, data))

    @delete(
        get_path(f"/roles/{IDENTIFIER_URI}", PREFIX),
        return_dto=role_read_dto,
        status_code=200,
        guards=guards,
    )
    async def delete_role(self, id_: UUID, service: UserServiceType) -> RoleT:
        """Delete a role from the database."""
        return cast(RoleT, await service.delete_role(id_))


    @put(
        get_path(f"/roles/assign", PREFIX),
        return_dto=user_read_dto,
        guards=guards,
    )
    async def assign_role(self, data: UserRoleSchema, service: UserServiceType) -> UserT:
        """Assign a role to a user."""
        return cast(UserT, await service.assign_role(data.user_id, data.role_id))


    @put(
        get_path(f"/roles/revoke", PREFIX),
        return_dto=user_read_dto
    )
    async def revoke_role(self, data: UserRoleSchema, service: UserServiceType) -> UserT:
        """Revoke a role from a user."""
        return cast(UserT, await service.revoke_role(data.user_id, data.role_id))
