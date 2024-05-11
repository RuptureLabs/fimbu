"""
Global fimbu exception and warning classes.
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Any
from litestar.exceptions import (
    HTTPException,
)
from litestar.status_codes import HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR
from structlog.contextvars import bind_contextvars
from click import ClickException
from litestar.exceptions import ImproperlyConfiguredException


if TYPE_CHECKING:
    from typing import Any
    from litestar.types import Scope




__all__ = (
    "AuthorizationError",
    "HealthCheckConfigurationError",
    "ApplicationError",
    "after_exception_hook_handler",
)


class FimbuException(Exception):
    detail: str

    def __init__(self, *args: Any, detail: str = "") -> None:
        """Initialize ``AdvancedAlchemyException``.

        Args:
            *args: args are converted to :class:`str` before passing to :class:`Exception`
            detail: detail of the exception.
        """
        str_args = [str(arg) for arg in args if arg]
        if not detail:
            if str_args:
                detail, *str_args = str_args
            elif hasattr(self, "detail"):
                detail = self.detail
        self.detail = detail
        super().__init__(*str_args)


    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__


    def __str__(self) -> str:
        return " ".join((*self.args, self.detail)).strip()


class CommandError(ClickException, FimbuException):...

class ImproperlyConfigured(FimbuException, ImproperlyConfiguredException):...

class LoadMiddlewareError(FimbuException):...

class AppRegistryNotReady(FimbuException):...

class SuspiciousFileOperation(FimbuException):...



class ApplicationError(Exception):
    """Base exception type for the lib's custom exception types."""

    detail: str

    def __init__(self, *args: Any, detail: str = "") -> None:
        """Initialize ``AdvancedAlchemyException``.

        Args:
            *args: args are converted to :class:`str` before passing to :class:`Exception`
            detail: detail of the exception.
        """
        str_args = [str(arg) for arg in args if arg]
        if not detail:
            if str_args:
                detail, *str_args = str_args
            elif hasattr(self, "detail"):
                detail = self.detail
        self.detail = detail
        super().__init__(*str_args)

    def __repr__(self) -> str:
        if self.detail:
            return f"{self.__class__.__name__} - {self.detail}"
        return self.__class__.__name__

    def __str__(self) -> str:
        return " ".join((*self.args, self.detail)).strip()


class MissingDependencyError(ApplicationError, ImportError):
    """Missing optional dependency.

    This exception is raised only when a module depends on a dependency that has not been installed.
    """


class ApplicationClientError(ApplicationError):
    """Base exception type for client errors."""


class AuthorizationError(ApplicationClientError):
    """A user tried to do something they shouldn't have."""


class HealthCheckConfigurationError(ApplicationError):
    """An error occurred while registering an health check."""


class _HTTPConflictException(HTTPException):
    """Request conflict with the current state of the target resource."""

    status_code = HTTP_409_CONFLICT


async def after_exception_hook_handler(exc: Exception, _scope: Scope) -> None:
    """Binds `exc_info` key with exception instance as value to structlog
    context vars.

    This must be a coroutine so that it is not wrapped in a thread where we'll lose context.

    Args:
        exc: the exception that was raised.
        _scope: scope of the request
    """
    if isinstance(exc, ApplicationError):
        return
    if isinstance(exc, HTTPException) and exc.status_code < HTTP_500_INTERNAL_SERVER_ERROR:
        return
    bind_contextvars(exc_info=sys.exc_info())
