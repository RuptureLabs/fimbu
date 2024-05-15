from __future__ import annotations


from functools import lru_cache
from typing import TYPE_CHECKING, Any

from fimbu.conf import settings
from fimbu.contrib.auth.protocols import UserT
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.utils.module_loading import import_string


if TYPE_CHECKING:
    from litestar import Litestar
    from litestar.contrib.jwt import JWTAuth, JWTCookieAuth
    from litestar.security.session_auth.auth import SessionAuth
    from fimbu.contrib.auth import AuthPlugin
    from fimbu.contrib.auth.service import BaseUserService


__all__ = [
    "get_auth_plugin",
    "get_auth_backend",
    "get_user_service",
    "get_user_model",
    "get_path",
    "get_auth_config",
    "has_custom_model",
    "installed_native_auth",
]

def get_auth_plugin(app: Litestar) -> AuthPlugin:
    """Get the AuthPlugin from the Litestar application."""
    from fimbu.contrib.auth import AuthPlugin

    try:
        return app.plugins.get(AuthPlugin)
    except KeyError as e:
        raise ImproperlyConfigured("The AuthPlugin is missing from the application") from e
    

def get_auth_backend(app: Litestar) -> JWTCookieAuth | JWTAuth | SessionAuth:
    return get_auth_plugin(app)._config.auth_backend


def get_user_service(app: Litestar) -> BaseUserService[Any, Any]:
    """Get a `UserService` instance outside of a Litestar request context."""
    from fimbu.contrib.auth.repository import RoleRepository

    config = get_auth_plugin(app)._config

    user_repository = config.user_repository_class(config.user_model)
    
    return config.user_service_class(
        user_repository=user_repository,
        secret=config.secret,
        hash_schemes=config.hash_schemes,
    )


def get_user_model() -> UserT:
    """Get the user model from the settings."""
    if hasattr(settings, 'USER_MODEL'):
        user_model = import_string(settings.USER_MODEL)
    else:
        from fimbu.contrib.auth.models import User
        user_model = User
    return user_model


def get_path(path: str, prefix: str = "") -> str:
    if prefix:
        return prefix.rstrip('/') + "/" + path.lstrip("/")
    return path


@lru_cache
def get_auth_config(attribute: str) -> Any:
    return import_string(getattr(settings, attribute))


def has_custom_model() -> bool:
    """Check if app as a custom model"""
    return settings.USER_MODEL != 'fimbu.contrib.auth.models.User'


def installed_native_auth() -> bool:
    """Check if settings.INSTALLED_APPs contains fimbu.contrib.auth"""
    return 'fimbu.contrib.auth' in settings.INSTALLED_APPS
