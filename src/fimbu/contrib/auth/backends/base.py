from __future__ import annotations

from typing import Any, Coroutine, Sequence, TYPE_CHECKING
from litestar.connection import ASGIConnection
from litestar.middleware.authentication import (
    AbstractAuthenticationMiddleware,
    AuthenticationResult,
)
from litestar import Request
from litestar.types import ASGIApp, Scopes
from litestar.exceptions import NotAuthorizedException

from fimbu.contrib.auth.protocols import UserT
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.contrib.auth.service import UserServiceType
from fimbu.contrib.auth.schemas import AccountLogin


if TYPE_CHECKING:
    from typing import Callable



__all__ = ["AuthenticationBackend"]



class AuthenticationBackend:

    def __init__(self, app: Callable, name: str, middleware: AbstractAuthenticationMiddleware) -> None:
        self._app = app
        self._name : str = name
        self._middleware: AbstractAuthenticationMiddleware = middleware

    @property
    def is_requested_backend(self, request: Request) -> bool:
        return request.query_params.get("auth_backend") == self._name
    

    async def login(self, request: Request, data: AccountLogin, service: UserServiceType):
        pass


    async def logout(self):
        pass


    async def retrieve_user(self):
        pass


    async def authenticate_request(self, connection: ASGIConnection) -> Coroutine[Any, Any, AuthenticationResult]:
        pass



class AuthenticationManagerMiddleware(AbstractAuthenticationMiddleware):
    def __init__(self, app: Callable, *args, **kwargs) -> None:
        super().__init__(app, *args, **kwargs)
        self._backends: list[AuthenticationBackend] = []
        self._backend: AuthenticationBackend | None= None
        self._default_backend: str | None = None
        """The authentication backend, can be set as a query parameter.
        e.g ?auth_backend=session"""

        self.checks()   # Checks the correct configuration of the middleware.


    def add_backend(self, backend: AuthenticationBackend, as_default: bool = False) -> None:
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
    

    def get_default_backend(self) -> AuthenticationBackend | None:
        """
        Returns the default authentication backend.
        """
        if self._default_backend:
            return self.get_backend(self._default_backend)


    def get_backend(self, name: str) -> AuthenticationBackend | None:
        """
        Returns an authentication backend by name.
        """
        for backend in self._backends:
            if backend.get_name() == name:
                return backend
            

    def get_requested_backend(self, request: Request) -> AuthenticationBackend | None:
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


    async def authenticate_request(self, connection: ASGIConnection) -> Coroutine[Any, Any, AuthenticationResult]:
        """
        Authenticates a request.
        """
        try:
            if self._default_backend:
                self._backend = self.get_backend(self._default_backend)
                return self._backend.authenticate_request(connection)
            
        except NotAuthorizedException as exc:
            
            for backend in self._backends:
                if backend.get_name() == self._default_backend:
                    continue
                
                try:
                    self._backend = backend
                    return self._backend.authenticate_request(connection)
                except NotAuthorizedException:
                    continue

        raise NotAuthorizedException() from exc
