import logging
from litestar.logging.config import LoggingConfig, StructLoggingConfig
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin

from fimbu.conf import settings
from fimbu.core.types import ApplicationType


__all__ = ["install_logger_plugin"]


def install_logger_plugin(app: ApplicationType) -> None:
    """Install logger plugin."""
    log = StructlogConfig(
        structlog_logging_config=StructLoggingConfig(
            log_exceptions="always",
            traceback_line_limit=4,
            standard_lib_logging_config=LoggingConfig(
                root={"level": logging.getLevelName(settings.LOG_LEVEL), "handlers": ["queue_listener"]},
                loggers={
                    "uvicorn.access": {
                        "propagate": False,
                        "level": settings.LOG_UVICORN_ACCESS_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                    "uvicorn.error": {
                        "propagate": False,
                        "level": settings.LOG_UVICORN_ERROR_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                    "granian.access": {
                        "propagate": False,
                        "level": settings.LOG_GRANIAN_ACCESS_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                    "granian.error": {
                        "propagate": False,
                        "level": settings.LOG_GRANIAN_ERROR_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                    "saq": {
                        "propagate": False,
                        "level": settings.LOG_SAQ_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                    "sqlalchemy.engine": {
                        "propagate": False,
                        "level": settings.LOG_SQLALCHEMY_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                    "sqlalchemy.pool": {
                        "propagate": False,
                        "level": settings.LOG_SQLALCHEMY_LEVEL,
                        "handlers": ["queue_listener"],
                    },
                },
            ),
        ),
        middleware_logging_config=LoggingMiddlewareConfig(
            request_log_fields=["method", "path", "path_params", "query"],
            response_log_fields=["status_code"],
        ),
    )

    structlog = StructlogPlugin(config=log)

    if isinstance(app, ApplicationType):
        app.set_config(
            'plugins',
            [structlog]
        )
    else:
        raise TypeError("app must be an instance or Application")
