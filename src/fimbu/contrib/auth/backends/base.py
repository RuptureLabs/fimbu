from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Coroutine, Sequence, TYPE_CHECKING, Self
from litestar.connection import ASGIConnection
from litestar.config.app import AppConfig
from litestar.middleware import DefineMiddleware
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar import Request
from litestar.exceptions import NotAuthorizedException
from litestar.middleware._utils import (
    should_bypass_middleware,
)

from fimbu.contrib.auth.protocols import UserT
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.contrib.auth.service import UserServiceType
from fimbu.contrib.auth.schemas import AccountLogin


if TYPE_CHECKING:
    from typing import Callable
    from litestar.types import Send, Scope, Receive



__all__ = ["AbstractAuthenticationBackend"]



class AbstractAuthenticationBackend(ABC):

    def __init__(self, app: Callable, name: str, middleware: AbstractAuthenticationMiddleware) -> None:
        self._app = app
        self._name : str = name
        self._middleware: AbstractAuthenticationMiddleware = middleware

    @property
    def is_requested_backend(self, request: Request) -> bool:
        return request.query_params.get("auth_backend") == self._name
    

    @abstractmethod
    async def login(self, request: Request, data: AccountLogin, service: UserServiceType):
        """
        Authenticates a user.

        request:
            Request : Request object

        data:
            AccountLogin : Login data

        service:
            UserServiceType : UserService object

        Raises: NotAuthorizedException
        """
        raise NotImplementedError


    @abstractmethod
    async def logout(self):
        """Logs out a user."""
        raise NotImplementedError


    @abstractmethod
    async def retrieve_user(self):
        """Retrieves a user."""
        raise NotImplementedError


    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        return self._middleware(scope, receive, send)


    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        return app_config



class AuthenticationMiddleware(AbstractAuthenticationMiddleware):
    def __init__(
            self, app: Callable, 
            default_backend: str | None = None,
            backends: Sequence[AbstractAuthenticationBackend] | None = None
            , **kwargs) -> None:
        super().__init__(app, **kwargs)
        self._backends: list[AbstractAuthenticationBackend] | None = backends
        self._backend: AbstractAuthenticationBackend | None= None
        self._default_backend: str | None = None
        """The authentication backend, can be set as a query parameter.
        e.g ?auth_backend=session"""

        self.checks()   # Checks the correct configuration of the middleware.


    def add_backend(self, backend: AbstractAuthenticationBackend, as_default: bool = False) -> None:
        """
        Adds an authentication backend.
        """
        self._backends.append(backend)
        if as_default:
            self._default_backend = backend.get_name()


    def checks(self):
        """
        Checks if the middleware is enabled.
        """
        if not self._backends:
            raise ImproperlyConfigured("No authentication backend has been added.")
        
        if self._default_backend and self.get_backend(self._default_backend) is None:
            raise ImproperlyConfigured("The default authentication backend does not exist.")
        

    @classmethod
    def build_middleware(cls, 
            default_backend: str | None = None,
            backends: Sequence[AbstractAuthenticationBackend] | None = None) -> Self:
        """
        Builds the authentication middleware.
        """
        return DefineMiddleware(
            cls,
            default_backend = default_backend,
            backends = backends
        )
        

    def get_backends(self) -> Sequence[AbstractAuthenticationBackend]:
        """
        Returns all authentication backends.
        """
        return self._backends
    

    @property
    def backend(self):
        return self._backend
    

    def get_default_backend(self) -> AbstractAuthenticationBackend | None:
        """
        Returns the default authentication backend.
        """
        if self._default_backend:
            return self.get_backend(self._default_backend)


    def get_backend(self, name: str) -> AbstractAuthenticationBackend | None:
        """
        Returns an authentication backend by name.
        """
        for backend in self._backends:
            if backend.get_name() == name:
                return backend
            

    def get_requested_backend(self, request: Request) -> AbstractAuthenticationBackend | None:
        """
        Returns the requested authentication backend.
        """
        for backend in self._backends:
            if backend.is_requested_backend(request):
                return backend


    async def login(self, request: Request, data: AccountLogin, service: UserServiceType):
        """
        Authenticates a user.

        If no backend is set, the default backend is used.

        Raises: NotAuthorizedException
        """
        self._backend = self.get_requested_backend(request)

        if self._backend:
            return await self._backend.login(request, data, service)
        

        if self._default_backend:
            self._backend = self.get_backend(self._default_backend)
            if self._backend:
                return await self._backend.login(request, data, service)
            
        raise NotAuthorizedException(detail="login failed, invalid input")


    async def logout(self, request: Request, **kwargs):
        """
        Logs out a user.

        If no backend is set, the default backend is used.
        """

        self._backend = self._backend if self._backend else self.get_default_backend()

        if self._backend:
            await self._backend.logout(request, **kwargs)


    async def retrieve_user(self, connection: ASGIConnection, **kwargs) -> UserT | None:
        """
        Retrieves a user.

        If no backend is set, the default backend is used.
        """

        self._backend = self._backend if self._backend else self.get_default_backend()
        if self._backend:
            return await self._backend.retrieve_user(connection, **kwargs)
        

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """ASGI callable.

        Args:
            scope: The ASGI connection scope.
            receive: The ASGI receive function.
            send: The ASGI send function.

        Returns:
            None
        """
        if not should_bypass_middleware(
            exclude_http_methods=self.exclude_http_methods,
            exclude_opt_key=self.exclude_opt_key,
            exclude_path_pattern=self.exclude,
            scope=scope,
            scopes=self.scopes,
        ):
            auth_result = await self.authenticate_request(scope, receive, send)
            scope["user"] = auth_result.user
            scope["auth"] = auth_result.auth
        await self.app(scope, receive, send)


    async def authenticate_request(self, scope: Scope, receive: Receive, send: Send) -> Coroutine[Any, Any, AuthenticationResult]:
        """
        Authenticates a request.
        """
        try:
            if self._default_backend:
                self._backend = self.get_backend(self._default_backend)
                await self._backend(scope, receive, send)
                return AuthenticationResult(
                    user=scope["user"], 
                    auth=scope["auth"]
                )
        except NotAuthorizedException as exc:
            
            for backend in self._backends:
                if backend.get_name() == self._default_backend:
                    continue
                
                try:
                    self._backend = backend
                    await self._backend(scope, receive, send)
                    return AuthenticationResult(
                        user=scope["user"], 
                        auth=scope["auth"]
                    )
                except NotAuthorizedException:
                    continue

        raise NotAuthorizedException() from exc
