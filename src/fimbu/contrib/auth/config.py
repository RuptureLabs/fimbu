from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Generic

from litestar.exceptions import ImproperlyConfiguredException
from litestar.security.session_auth import SessionAuth

from fimbu.contrib.auth.repository import UserRepository
from fimbu.contrib.auth.protocols import  UserT

__all__ = [
    "AuthConfig",
]

if TYPE_CHECKING:
    from litestar.contrib.jwt import JWTAuth, JWTCookieAuth
    from litestar.middleware.session.base import BaseBackendConfig
    from litestar.stores.redis import RedisStore
    from fimbu.contrib.auth.service import BaseUserService
    from fimbu.contrib.auth.backends.base import AbstractAuthenticationBackend




@dataclass
class AuthConfig(Generic[UserT]):
    """Configuration class for LitestarUsers."""

    auth_backend: str
    """The authentication backend to use by default."""
    auth_backends : list[AbstractAuthenticationBackend]
    """List of authentication backends."""
    secret: str
    """Secret string for securely signing tokens."""
    user_model: type[UserT]
    """A subclass of a `User` ORM model."""
    user_service_class: type[BaseUserService]
    """A subclass of [BaseUserService][litestar_users.service.BaseUserService]."""

    user_repository_class: type[UserRepository] = UserRepository
    """The user repository class to use."""
    auth_exclude_paths: list[str] = field(default_factory=lambda: ["/schema"])
    """Paths to be excluded from authentication checks."""
    auth_backend: type[JWTAuth | JWTCookieAuth | SessionAuth] | None = None
    """Authentication backend"""
    auth_store : RedisStore | None = None
    """Auth store used for cache strategy"""
    hash_schemes: list[str] = field(default_factory=lambda: ["argon2"])
    """Schemes to use for password encryption.

    Defaults to `["argon2"]`
    """
    

    def __post_init__(self) -> None:
        """Validate the configuration.

        - A session backend must be configured if `auth_backend_class` is `SessionAuth`.
        """

        if len(self.secret) not in [16, 24, 32]:
            raise ImproperlyConfiguredException("secret must be 16, 24 or 32 characters")
