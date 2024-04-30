from __future__ import annotations

from typing import TYPE_CHECKING, Any

from fimbu.conf import settings
from fimbu.contrib.auth.protocols import UserT
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.contrib.auth.adapters.repository import RoleRepository
from fimbu.utils.module_loading import import_string


if TYPE_CHECKING:
    from litestar import Litestar

    from fimbu.contrib.auth import AuthPlugin
    from fimbu.contrib.auth.service import BaseUserService


def get_auth_plugin(app: Litestar) -> AuthPlugin:
    """Get the AuthPlugin from the Litestar application."""
    from fimbu.contrib.auth import AuthPlugin

    try:
        return app.plugins.get(AuthPlugin)
    except KeyError as e:
        raise ImproperlyConfigured("The AuthPlugin is missing from the application") from e


def get_user_service(app: Litestar) -> BaseUserService[Any, Any]:
    """Get a `UserService` instance outside of a Litestar request context."""

    config = get_auth_plugin(app)._config

    user_repository = config.user_repository_class(config.user_model)
    role_repository: RoleRepository | None = (
        RoleRepository(config.role_model) if config.role_model else None
    )
    return config.user_service_class(
        user_repository=user_repository,
        role_repository=role_repository,
        secret=config.secret,
        hash_schemes=config.hash_schemes,
    )

def get_user_model() -> UserT:
    """Get the user model from the settings."""
    if hasattr(settings, 'USER_MODEL'):
        print(settings.USER_MODEL, '------------')
        user_model = import_string(settings.USER_MODEL)
    else:
        from fimbu.contrib.auth.models import User
        user_model = User
    return user_model
