import functools

from litestar.datastructures import MutableScopeHeaders
from litestar.middleware.base import AbstractMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware(AbstractMiddleware):
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":  # pragma: no cover
            await self.app(scope, receive, send)
            return

        send = functools.partial(self.send, send=send, scope=scope)
        await self.app(scope, receive, send)

    async def send(self, message: Message, send: Send, scope: Scope) -> None:
        if message["type"] != "http.response.start":
            await send(message)
            return

        message.setdefault("headers", [])
        headers = MutableScopeHeaders(scope=message)

        headers.add("content-security-policy", "frame-ancestors 'self'")
        headers.add("x-frame-options", "SAMEORIGIN")
        headers.add("referrer-policy", "strict-origin-when-cross-origin")
        headers.add("x-content-type-options", "nosniff")
        headers.add("permissions-policy", "geolocation=(), camera=(), microphone=()")

        await send(message)
