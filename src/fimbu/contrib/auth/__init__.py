from __future__ import annotations

from fimbu.contrib.auth.utils import get_auth_config, get_user_model
from fimbu.db.exceptions import RepositoryError
from litestar.contrib.jwt import JWTAuth, JWTCookieAuth, OAuth2PasswordBearerAuth
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol
from litestar.security.session_auth import SessionAuth

from click import Group
from litestar.config.app import AppConfig
from litestar.types import ExceptionHandlersMap
from fimbu.contrib.auth.config import AuthConfig

from fimbu.conf import settings
from fimbu.core.types import ApplicationType
from fimbu.contrib.auth.exceptions import (
    TokenException,
    repository_exception_to_http_response,
    token_exception_handler
)

from fimbu.contrib.auth.retrieve_user import (
    jwt_retrieve_user_handler,
    session_retrieve_user_handler,
)


__all__ = ["AuthPlugin", "AuthConfig", "install_auth_plugin"]


class AuthPlugin(InitPluginProtocol, CLIPluginProtocol):
    """A Litestar extension for authentication, authorization and user management."""

    def __init__(self, config: AuthConfig) -> None:
        """Construct a LitestarUsers instance."""
        self._config = config

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Register routers, auth strategies etc on the Litestar app.

        Args:
            app_config: An instance of [AppConfig][litestar.config.AppConfig]
        """
        auth_backend = self._get_auth_backend()

        app_config = auth_backend.on_app_init(app_config)

        exception_handlers: ExceptionHandlersMap = {
            RepositoryError: repository_exception_to_http_response,  # type: ignore[dict-item]
            TokenException: token_exception_handler,  # type: ignore[dict-item]
        }
        app_config.exception_handlers.update(exception_handlers)
        app_config.state.update({"auth_config": self._config})

        return app_config

    def on_cli_init(self, cli: Group) -> None:
        from fimbu.contrib.auth.cli import user_management_group

        cli.add_command(user_management_group)
        return super().on_cli_init(cli)

    def _get_auth_backend(self) -> JWTAuth | JWTCookieAuth | SessionAuth | OAuth2PasswordBearerAuth:
        if issubclass(self._config.auth_backend_class, SessionAuth):
            self._config.auth_backend = self._config.auth_backend_class[self._config.user_model, type(self._config.session_backend_config)](
                retrieve_user_handler=session_retrieve_user_handler,  # type: ignore[arg-type]
                session_backend_config=self._config.session_backend_config,  # type: ignore
                exclude=settings.AUTH_EXCLUDE_PATHS,
            )

            return self._config.auth_backend
        
        elif issubclass(self._config.auth_backend_class, OAuth2PasswordBearerAuth):
            self._config.auth_backend = self._config.auth_backend_class[self._config.user_model](
                retrieve_user_handler=jwt_retrieve_user_handler,
                token_secret=self._config.secret,
                token_url="/auth/login",
                exclude=settings.AUTH_EXCLUDE_PATHS,
            )

            return self._config.auth_backend

        elif issubclass(self._config.auth_backend_class, JWTAuth) or issubclass(
            self._config.auth_backend_class, JWTCookieAuth
        ):
            self._config.auth_backend = self._config.auth_backend_class(
                retrieve_user_handler=jwt_retrieve_user_handler,
                token_secret=self._config.secret,
                exclude=settings.AUTH_EXCLUDE_PATHS,
            )

            return self._config.auth_backend
        
        raise ValueError("invalid auth backend")


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
