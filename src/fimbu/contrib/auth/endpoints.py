from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from uuid import UUID

from litestar import (
    Request,
    Response,
    delete,
    get,
    patch,
    post,
    put,
)
from litestar.contrib.jwt import JWTAuth, JWTCookieAuth
from litestar.di import Provide
from litestar.exceptions import ImproperlyConfiguredException, NotAuthorizedException, PermissionDeniedException
from litestar.security.session_auth.auth import SessionAuth

from fimbu.conf import settings
from fimbu.contrib.auth.adapters.protocols import RoleT, UserT
from fimbu.contrib.auth.dependencies import provide_user_service
from fimbu.contrib.auth.schema import RoleSchema, UserRegistrationSchema, UserSchema
from fimbu.contrib.auth.utils import get_path, get_auth_config, get_auth_backend


from litestar.contrib.pydantic import PydanticDTO
from litestar.dto import DTOData
from litestar.types import Guard

from fimbu.contrib.auth.protocols import UserRegisterT
from fimbu.contrib.auth.schema import (
    AuthenticationSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    UserRoleSchema,
)
from fimbu.contrib.auth.service import UserServiceType


IDENTIFIER_URI = settings.AUTH_UUID_IDENTIFIERS
PREFIX: str = settings.AUTH_PREFIX
TAGS: list[str] = settings.AUTH_TAGS


_auth_backend: JWTCookieAuth | JWTAuth | SessionAuth = get_auth_config("AUTH_BACKEND_CLASS")
user_read_dto: PydanticDTO = get_auth_config("USER_READ_DTO")
user_registration_dto: PydanticDTO = get_auth_config("USER_REGISTRATION_DTO")
user_update_dto: PydanticDTO = get_auth_config("USER_UPDATE_DTO")
role_create_dto: PydanticDTO = get_auth_config("ROLE_CREATE_DTO")
role_read_dto: PydanticDTO = get_auth_config("ROLE_READ_DTO")
role_update_dto: PydanticDTO = get_auth_config("ROLE_UPDATE_DTO")
guards: list[Guard] = settings.AUTH_GUARDS


@post(
    get_path("/register", PREFIX),
    dto=user_registration_dto,
    return_dto=user_read_dto,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    exclude_from_auth=True,
    exclude_from_csrf=True,
    tags=TAGS,
)
async def register(data: UserRegistrationSchema, service: UserServiceType, request: Request) -> UserT:
    """Register a new user."""
    d = {
        "user_name": "edimedia",
        "first_name": "edimedia",
        "last_name": "edimedia",
    }
    d.update(data.model_dump())
    return cast(UserT, await service.register(d, request))


@post(
    get_path("/verify", PREFIX),
    return_dto=user_read_dto,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    exclude_from_auth=True,
    tags=TAGS,
)
async def verify(token: str, service: UserServiceType, request: Request) -> UserT:
    """Verify a user with a given JWT."""

    return cast(UserT, await service.verify(token, request))


@post(
    get_path("/login", PREFIX,),
    return_dto=user_read_dto,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    exclude_from_auth=True,
    tags=TAGS,
    exclude_from_csrf=True,
)
async def login_session(data: AuthenticationSchema, service: UserServiceType, request: Request) -> UserT:
    """Authenticate a user."""
    auth_backend = get_auth_backend(request.app)
    if not isinstance(auth_backend, SessionAuth):
        raise ImproperlyConfiguredException("session login can only be used with SesssionAuth")

    user = await service.authenticate(data, request)
    if user is None:
        request.clear_session()
        raise NotAuthorizedException(detail="login failed, invalid input")

    request.set_session({"user_id": user.id})  # TODO: move and make configurable
    return cast(UserT, user)

@post(
    get_path("/login", PREFIX),
    return_dto=user_read_dto,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    exclude_from_auth=True,
    tags=TAGS,
)
async def login_jwt(data: AuthenticationSchema, service: UserServiceType, request: Request) -> Response[UserT]:
    """Authenticate a user."""
    auth_backend = get_auth_backend(request.app)
    if not isinstance(auth_backend, (JWTAuth, JWTCookieAuth)):
        raise ImproperlyConfiguredException("jwt login can only be used with JWTAuth")

    user = await service.authenticate(data, request)
    if user is None:
        raise NotAuthorizedException(detail="login failed, invalid input")

    if user.is_verified is False:
        raise PermissionDeniedException(detail="not verified")

    return auth_backend.login(identifier=str(user.id), response_body=cast(UserT, user))


@post(get_path("/logout", PREFIX), tags=TAGS)
async def logout(request: Request) -> None:
    """Log an authenticated user out."""
    request.clear_session()


@get(get_path("/users/me", PREFIX), return_dto=user_read_dto, tags=TAGS)
async def get_current_user(request: Request[UserT, Any, Any]) -> UserT:
    """Get current user info."""

    return request.user

@patch(
    get_path("/users/me", PREFIX),
    dto=user_update_dto,
    return_dto=user_read_dto,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def update_current_user(
    data: UserSchema,
    request: Request[UserT, Any, Any],
    service: UserServiceType,
) -> UserT:
    """Update the current user."""
    data.id = request.user.id
    return cast(UserT, await service.update_user(data=data))


@post(
    get_path("/forgot-password", PREFIX),
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    exclude_from_auth=True,
    tags=TAGS,
)
async def forgot_password(data: ForgotPasswordSchema, service: UserServiceType) -> None:
    await service.initiate_password_reset(data.email)
    return

@post(
    get_path("/reset-password", PREFIX),
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    exclude_from_auth=True,
    tags=TAGS,
)
async def reset_password(data: ResetPasswordSchema, service: UserServiceType) -> None:
    await service.reset_password(data.token, data.password)
    return



@get(
    get_path(f"/users/{IDENTIFIER_URI}", PREFIX),
    dto=user_read_dto,
    return_dto=user_read_dto,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def get_user(id_: UUID, service: UserServiceType) -> UserT:
    """Get a user by id."""

    return cast(UserT, await service.get_user(id_))

@patch(
    get_path(f"/users/{IDENTIFIER_URI}", PREFIX),
    dto=user_update_dto,
    return_dto=user_read_dto,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def update_user(id_: UUID, data: UserSchema, service: UserServiceType) -> UserT:
    """Update a user's attributes."""
    data.id = id_
    return cast(UserSchema, await service.update_user(data))


@delete(
    get_path(f"/users/{IDENTIFIER_URI}", PREFIX),
    return_dto=user_read_dto,
    status_code=200,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def delete_user(id_: UUID, service: UserServiceType) -> UserT:
    """Delete a user from the database."""

    return cast(UserT, await service.delete_user(id_))


@post(
    get_path("/roles", PREFIX),
    dto=role_create_dto,
    return_dto=role_read_dto,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def create_role(data: RoleSchema, service: UserServiceType) -> RoleSchema:
    """Create a new role."""
    return cast(RoleT, await service.add_role(data))

@patch(
    get_path(f"/roles/{IDENTIFIER_URI}", PREFIX),
    dto=role_update_dto,
    return_dto=role_read_dto,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def update_role(id_: UUID, data: UserRoleSchema, service: UserServiceType) -> RoleT:
    """Update a role in the database."""
    data.id = id_
    return cast(RoleT, await service.update_role(id_, data))

@delete(
    get_path(f"/roles/{IDENTIFIER_URI}", PREFIX),
    return_dto=role_read_dto,
    status_code=200,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def delete_role(id_: UUID, service: UserServiceType) -> RoleT:
    """Delete a role from the database."""

    return cast(RoleT, await service.delete_role(id_))


@put(
    get_path(f"/roles/assign", PREFIX),
    return_dto=user_read_dto,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def assign_role(data: UserRoleSchema, service: UserServiceType) -> UserT:
    """Assign a role to a user."""

    return cast(UserT, await service.assign_role(data.user_id, data.role_id))


@put(
    get_path(f"/roles/revoke", PREFIX),
    return_dto=user_read_dto,
    guards=guards,
    dependencies={"service": Provide(provide_user_service, sync_to_thread=False)},
    tags=TAGS,
)
async def revoke_role(data: UserRoleSchema, service: UserServiceType) -> UserT:
    """Revoke a role from a user."""

    return cast(UserT, await service.revoke_role(data.user_id, data.role_id))



__handlers__ = [
    get_current_user, update_current_user, 
    forgot_password, reset_password,get_user, 
    update_user, delete_user, create_role, update_role,
    delete_role, assign_role, revoke_role, register,
]

if  (_auth_backend is SessionAuth) or isinstance(_auth_backend, SessionAuth):
    __handlers__.extend([login_session, logout])
else:
    __handlers__.append(login_jwt)
