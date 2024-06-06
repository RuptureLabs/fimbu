
from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from litestar.plugins import InitPluginProtocol
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry

from redis.asyncio import Redis
from fimbu.conf import settings
from fimbu.utils.text import slugify


if TYPE_CHECKING:
    from litestar.config.app import AppConfig



__all__ = [
    "get_redis", 
    "FRedis",
    "RedisFactory",
]

T = TypeVar("T")

class FRedis:
    _redis_instance: Redis | None = None
    """Redis instance generated from settings."""

    @property
    def client(self) -> Redis:
        return self.get_client()

    def get_client(self) -> Redis:
        if self._redis_instance is not None:
            return self._redis_instance
        self._redis_instance = Redis.from_url(
            url=settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=False,
            socket_connect_timeout=settings.REDIS_SOCKET_CONNECT_TIMEOUT,
            socket_keepalive=settings.REDIS_SOCKET_KEEPALIVE,
            health_check_interval=settings.REDIS_HEALTH_CHECK_INTERVAL,
        )
        return self._redis_instance


def get_redis() -> Redis:
    """Get Redis instance."""
    return FRedis().client



class RedisFactory(InitPluginProtocol):
    """Application configuration plugin."""

    __slots__ = ("redis", "app_slug")
    redis: Redis
    app_slug: str

    def __init__(self) -> None:
        """Initialize ``RedisFactory``.
        """

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure application for use with redis.

        Args:
            app_config: The :class:`AppConfig <.config.app.AppConfig>` instance.
        """

        self.redis = get_redis()
        self.app_slug = slugify(settings.APP_NAME)
        app_config.stores = StoreRegistry(default_factory=self.redis_store_factory)
        app_config.on_shutdown.append(self.redis.aclose)  # type: ignore[attr-defined]
        
        return app_config

    def redis_store_factory(self, name: str) -> RedisStore:
        return RedisStore(self.redis, namespace=f"{self.app_slug}:{name}")
