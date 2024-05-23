# From litestar_utils By Alurith

from typing import TYPE_CHECKING

from litestar.datastructures import URL
from litestar.middleware.base import AbstractMiddleware
from litestar.response import Redirect
from litestar.status_codes import HTTP_307_TEMPORARY_REDIRECT

if TYPE_CHECKING:
    from litestar.types import ASGIApp, Receive, Scope, Send


class HTTPSRedirectMiddleware(AbstractMiddleware):
    """
    Redirect incoming requests from `http` or `ws` to `https` or `wss`.

    Ported from starlette: https://www.starlette.io/middleware/#httpsredirectmiddleware
    """

    def __init__(self, app: "ASGIApp") -> None:
        super().__init__(app)

    async def __call__(self, scope: "Scope", receive: "Receive", send: "Send") -> None:
        if scope["type"] in ("http", "websocket") and scope["scheme"] in ("http", "ws"):
            url = URL.from_scope(scope=scope)
            redirect_scheme = {"http": "https", "ws": "wss"}[url.scheme]
            netloc = url.hostname if url.port in (80, 443) else url.netloc
            url = url.with_replacements(scheme=redirect_scheme, netloc=netloc)
            response = Redirect(
                str(url), status_code=HTTP_307_TEMPORARY_REDIRECT
            )
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)
