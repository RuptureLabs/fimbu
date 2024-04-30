"""
Global fimbu exception and warning classes.
"""
from typing import Any
from click import ClickException
from litestar.exceptions import ImproperlyConfiguredException


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
