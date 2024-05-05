# From litestar_utils By Alurith

from time import time
from typing import TYPE_CHECKING, Callable, List, Optional, Type, Union

from litestar import Request
from litestar.middleware.base import AbstractMiddleware

if TYPE_CHECKING:
    from litestar.types import ASGIApp, Message, Receive, Scope, Scopes, Send

EmitCallable = Callable[[Request, float], None]


def create_timing_middleware(
    emit: EmitCallable,
    exclude: Optional[Union[str, List[str]]] = None,
    exclude_opt_key: Optional[str] = "exclude_timing",
    scopes: Optional["Scopes"] = None,
) -> Type[AbstractMiddleware]:
    """
    Basic function to create a timing middleware.

    emit: A Callable that accept two arguments, Request and float.

    exclude: A string or a list of strings of paths that are omitted.

    exclude_opt_key: A key to omit the middleware from a specific route.
    Default `exclude_timing`
    scopes:  Can be set to `ScopeType.HTTP` and `ScopeType.WEBSOCKET`.
    The default is both.

    For more informations about the fields check the Litestar docs [Creating Middleware](https://docs.litestar.dev/2/usage/middleware/creating-middleware.html)
    """

    class BaseTimingMiddleware(AbstractMiddleware):
        def __init__(self, app: "ASGIApp") -> None:
            super().__init__(app, exclude, exclude_opt_key, scopes)

        async def __call__(
            self, scope: "Scope", receive: "Receive", send: "Send"
        ) -> None:
            start_time = time()
            request: Request = Request(scope)

            async def send_wrapper(message: "Message") -> None:
                if message["type"] == "http.response.body":
                    emit(request, time() - start_time)
                await send(message)

            await self.app(
                scope,
                receive,
                send_wrapper,
            )

    return BaseTimingMiddleware
