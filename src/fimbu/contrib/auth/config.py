from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic

from litestar.exceptions import ImproperlyConfiguredException
from litestar.security.session_auth import SessionAuth

from fimbu.contrib.auth.repository import UserRepository
from fimbu.contrib.auth.protocols import RoleT, UserT

__all__ = [
    "AuthHandlerConfig",
    "CurrentUserHandlerConfig",
    "PasswordResetHandlerConfig",
    "RegisterHandlerConfig",
    "RoleManagementHandlerConfig",
    "AuthConfig",
    "UserManagementHandlerConfig",
    "VerificationHandlerConfig",
]

if TYPE_CHECKING:
    from litestar.contrib.jwt import JWTAuth, JWTCookieAuth
    from litestar.contrib.pydantic import PydanticDTO
    from litestar.dto import DataclassDTO, MsgspecDTO
    from litestar.middleware.session.base import BaseBackendConfig
    from litestar.types import Guard

    from fimbu.contrib.auth.service import BaseUserService




@dataclass
class AuthConfig(Generic[UserT, RoleT]):
    """Configuration class for LitestarUsers."""

    auth_backend_class: type[JWTAuth | JWTCookieAuth | SessionAuth]
    """The authentication backend to use by Litestar."""
    secret: str
    """Secret string for securely signing tokens."""
    user_model: type[UserT]
    """A subclass of a `User` ORM model."""
    user_service_class: type[BaseUserService]
    """A subclass of [BaseUserService][litestar_users.service.BaseUserService]."""
    user_registration_dto: type[DataclassDTO | MsgspecDTO | PydanticDTO]
    """DTO class user for user registration."""
    user_read_dto: type[PydanticDTO]
    """A `User` model based SQLAlchemy DTO class."""
    user_update_dto: type[PydanticDTO]
    """A `User` model based SQLAlchemy DTO class."""
    user_repository_class: type[UserRepository] = UserRepository
    """The user repository class to use."""
    auth_exclude_paths: list[str] = field(default_factory=lambda: ["/schema"])
    auth_backend: type[JWTAuth | JWTCookieAuth | SessionAuth] | None = None
    """Paths to be excluded from authentication checks."""
    hash_schemes: list[str] = field(default_factory=lambda: ["argon2"])
    """Schemes to use for password encryption.

    Defaults to `["argon2"]`
    """
    session_backend_config: BaseBackendConfig | None = None
    """Optional backend configuration for session based authentication.

    Notes:
        - Required if `auth_backend_class` is `SessionAuth`.
    """
    role_model: type[RoleT] | None = None
    """A `Role` ORM model.

    Notes:
        - Required if `role_management_handler_config` is set.
    """
    role_create_dto: type[PydanticDTO] | None = None
    """A `PydanticDTO` based on a `Role` ORM model.

    Notes:
        - Required if `role_management_handler_config` is set.
    """
    role_read_dto: type[PydanticDTO] | None = None
    """A `PydanticDTO` based on a `Role` ORM model.

    Notes:
        - Required if `role_management_handler_config` is set.
    """
    role_update_dto: type[PydanticDTO] | None = None
    """A `PydanticDTO` based on a `Role` ORM model.

    Notes:
        - Required if `role_management_handler_config` is set.
    """

    def __post_init__(self) -> None:
        """Validate the configuration.

        - A session backend must be configured if `auth_backend_class` is `SessionAuth`.
        """
        if self.auth_backend_class == SessionAuth and not self.session_backend_config:
            raise ImproperlyConfiguredException(
                'session_backend_config must be set when auth_backend is set to "session"'
            )

        if len(self.secret) not in [16, 24, 32]:
            raise ImproperlyConfiguredException("secret must be 16, 24 or 32 characters")
