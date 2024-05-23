from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from litestar.plugins import InitPluginProtocol
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry

from fimbu.conf import settings
from fimbu.utils.text import slugify
from fimbu.contrib.redis import get_redis

if TYPE_CHECKING:

    from litestar import Request
    from litestar.config.app import AppConfig
    from redis.asyncio import Redis


T = TypeVar("T")


class ApplicationConfigurator(InitPluginProtocol):
    """Application configuration plugin."""

    __slots__ = ("redis", "app_slug")
    redis: Redis
    app_slug: str

    def __init__(self) -> None:
        """Initialize ``ApplicationConfigurator``.

        Args:
            config: configure and start SAQ.
        """

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        """Configure application for use with SQLAlchemy.

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

