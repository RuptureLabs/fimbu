from __future__ import annotations

from typing import TYPE_CHECKING

from click import Group
from litestar.config.app import AppConfig
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol
from litestar.types import ExceptionHandlersMap
from fimbu.contrib.auth.config import AuthConfig
from fimbu.contrib.auth.utils import get_auth_config, get_user_model
from fimbu.db.exceptions import RepositoryError

from fimbu.conf import settings
from fimbu.core.types import ApplicationType
from fimbu.contrib.auth.exceptions import (
    TokenException,
    repository_exception_to_http_response,
    token_exception_handler
)

from fimbu.contrib.auth.backends.base import AuthenticationMiddleware

if TYPE_CHECKING:
    from fimbu.contrib.auth.backends.base import AuthenticationBackend


__all__ = ["AuthPlugin", "AuthConfig", "install_auth_plugin"]


class AuthPlugin(InitPluginProtocol, CLIPluginProtocol):
    """A Litestar extension for authentication, authorization and user management."""

    def __init__(self, config: AuthConfig) -> None:
        """Construct a LitestarUsers instance."""
        self._config = config
        self._auth_manager : AuthenticationMiddleware | None = None
        self._init()


    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Register routers, auth strategies etc on the Litestar app.

        Args:
            app_config: An instance of [AppConfig][litestar.config.AppConfig]
        """

        for backend in self._config.auth_backends:
            app_config = backend.on_app_init(app_config)


        app_config.middleware.insert(
            0, AuthenticationMiddleware.build_middleware(
                default_backend=self._config.auth_backend,
                backends=self._config.auth_backends 
            )
        )

        exception_handlers: ExceptionHandlersMap = {
            RepositoryError: repository_exception_to_http_response,  # type: ignore[dict-item]
            TokenException: token_exception_handler,  # type: ignore[dict-item]
        }
        app_config.exception_handlers.update(exception_handlers)
        app_config.state.update({"auth_config": self._config})

        self._config.auth_store = app_config.stores.get(settings.AUTH_STORE_KEY)

        return app_config


    def on_cli_init(self, cli: Group) -> None:
        from fimbu.contrib.auth.cli import user_management_group

        cli.add_command(user_management_group)
        return super().on_cli_init(cli)


    def get_auth_backend(self) -> AuthenticationBackend | None:
        """
        Returns:
            The authentication backend to use.
        """
        return self._auth_manager.backend



def install_auth_plugin(app: ApplicationType) -> None:
    """Install the authentication plugin."""
    
    auth_plugin = AuthPlugin(
        AuthConfig(
            auth_backend_class=get_auth_config("AUTH_BACKEND_CLASS"),
            session_backend_config=get_auth_config("SESSION_BACKEND_CONFIG")(),
            user_model=get_user_model(),
            secret=settings.SECRET,
            user_service_class=get_auth_config("USER_SERVICE_CLASS"),
            hash_schemes=settings.HASH_SCHEMES,
        )
    )

    if isinstance(app, ApplicationType):
        app.set_config(
            'plugins',
            [auth_plugin]
        )
    else:
        raise TypeError("app must be an instance or Application")
