from __future__ import annotations

from typing import Literal, Type, Any, TYPE_CHECKING
from pathlib import Path
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files.config import StaticFilesConfig
from litestar.middleware.compression import CompressionMiddleware


if TYPE_CHECKING:
    from litestar.data_extractors import RequestExtractorField, ResponseExtractorField
    from litestar.types import Scopes, Method


########## ------------------------------- FIMBU - PROJECT --------------------------------- ##########

BASE_DIR: Path = Path.cwd()
SECRET: str = 'fimbu_secret_key'
DEBUG: bool = True
APP_NAME: str = "fimbu"
LANGUAGE_CODE: str = 'en-us'
TIME_ZONE:str = 'UTC'
USE_I18N: str = True
USE_TZ: str = True

INSTALLED_APPS: list[str] = []

MIDDLEWARE: list[str] = []

MIDDLEWARE_FROM_FACTORY_BEFORE: str = False

ASGI_APPLICATION: str = 'fimbu.apps.main:app'


DATABASES: dict[str, Any] = [
    {
        "primary": True,
        "engine": "sqlite",
        "database": "database.db",
    },
]


# Templates

TEMPLATES : dict[str, Any] = {
    'DIRS' : ['templates'],
    'ENGINE' : JinjaTemplateEngine,
}


# Static files

STATIC_FILES: list[Any] = [
    {
        'DIRS': ['static'],
        'PATH' : "/static",
        'HTML_MODE' : False,
        'NAME' : "static",
        'AS_ATTACHMENT' : False
    },
    StaticFilesConfig(
        directories=["static"],
        path="/some_folder/static/path",
        html_mode=False,
        name="static",
        send_as_attachment=True,
    ),
]


APP_MIGRATIONS_FOLDER: str = 'migrations'

MIGRATIONS_LOCATION: str = BASE_DIR / APP_MIGRATIONS_FOLDER


####### -------------------------------- ALLOWED HOSTS CONFIG --------------------- #########

DISABLE_ALLOWED_HOSTS: bool = False
ALLOWED_HOSTS: list[str] = ['127.0.0.1']
EXCLUDE_HOSTS: str | list[str] | None = None  # exclude parameter from Litestar's AllowedHostsConfig
ALLOWED_HOSTS_EXCLUDE_OPT_KEY: str | None = None # exclude_opt_key parameter from Litestar's AllowedHostsConfig
ALLOWED_HOSTS_SCOPES: Type[Scopes] | None = None
WWW_REDIRECT: bool = True


####### -------------------------------- CORS CONFIG ------------------------------ ##########

DISABLE_CORS: bool = False
ALLOW_ORIGINS: list[str] = []
ALLOW_METHODS: list[str] = ['*']
ALLOW_HEADERS: list[str] = []
ALLOW_CREDENTIALS: bool = False
ALLOW_ORIGIN_REGEX: str | None = None
EXPOSE_HEADERS: list[str] = []
CORS_MAX_AGE: int = 600


##### -------------------------------- COMPRESSION CONFIG ------------------------- ###########

DISABLE_COMPRESSION: bool = False
COMPRESSION_BACKEND: Literal['gzip', 'brotli'] | None = None
COMPRESSION_MINIMUM_SIZE: int = 500
GZIP_COMPRESS_LEVEL: int = 9                                            # [0-9]
BROTLI_QUALITY: int = 6                                                 # [0-11]
BROTLI_MODE: Literal['generic', 'text', 'font'] = 'text'
BROTLI_LGWIN: int = 22                                                  # [10-24]
BROTLI_LGBLOCK: Literal[0, 16, 17, 18, 19, 20, 21, 22, 23, 24] = 0      # [16-24]
COMPRESSION_MIDDLEWARE_CLASS:Type[CompressionMiddleware] | None = None
COMPRESSION_EXCLUDE: str | list[str] | None = None
COMPRESSION_EXCLUDE_OPT_KEY: str | None = None


#### -------------------------------- CSRF CONFIG ---------------------------------- ###########

DISABLE_CSRF: bool = False
CSRF_COOKIE_NAME: str = 'csrftoken'
CSRF_COOKIE_PATH: str = '/'
CSRF_HEADER_NAME: str = 'x-csrftoken'
CSRF_COOKIE_SECURE: bool = False
CSRF_COOKIE_HTTPONLY: bool = False
CSRF_COOKIE_SAMESITE: Literal['lax', 'strict', 'none'] = 'lax'
CSRF_COOKIE_DOMAIN: str | None = None
CSRF_SAFE_METHODS: set[Method] = ('GET',)
CSRF_EXCLUDE: str | list[str] | None = None
EXCLUDE_FROM_CSRF_KEY: str = 'exclude_from_csrf'

#### ------------------------------- RESPONSE CACHE CONFIG ------------------------- ############

DISABLE_RESPONSE_CACHE = False
RESPONSE_CACHE_DEFAULT_EXPIRATION: int | None= 60
RESPONSE_CACHE_STORE_NAME: str = 'response_cache'


#### --------------------------------- EMAIL CONFIG ------------------------------- ###########

SERVER_EMAIL = "root@localhost"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "localhost"
EMAIL_PORT = 25
EMAIL_USE_LOCALTIME = False
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None
DEFAULT_FROM_EMAIL = "webmaster@localhost"
EMAIL_SUBJECT_PREFIX = "[Fimbu ] "


#### -------------------------------------- AUTHENTICATION ---------------------------- ###########

AUTH_BACKEND_CLASS = 'litestar.contrib.jwt.JWTCookieAuth'
SESSION_BACKEND_CONFIG = 'litestar.middleware.session.server_side.ServerSideSessionConfig'
USER_MODEL = 'fimbu.contrib.auth.models.User'

HASH_SCHEMES = ["argon2"]
AUTH_GUARDS = []
AUTH_CHECK_VERIFIED = True
AUTH_TAGS = []
AUTH_PREFIX = "/auth"
AUTH_EXCLUDE_PATHS = ['/schema',]
USER_SERVICE_CLASS = 'fimbu.contrib.auth.service.UserService'
USERS_REPOSITORY = 'fimbu.contrib.auth.adapters.repository.UserRepository'
USER_DEFAULT_ROLE = "Application Access"

# ----------------------------- SYSTEM HEALTH -----------------------------------------

SYSTEM_HEALTH_PATH: str = "/health"


# ----------------------------- SYSTEM LOG -------------------------------------------

LOG_EXCLUDE_PATHS: str = r"\A(?!x)x"
"""Regex to exclude paths from logging."""
LOG_HTTP_EVENT: str = "HTTP"
"""Log event name for logs from Litestar handlers."""
LOG_INCLUDE_COMPRESSED_BODY: bool = False
"""Include 'body' of compressed responses in log output."""
LOG_LEVEL: int = 10
"""Stdlib log levels.

Only emit logs at this level, or higher.
"""
LOG_OBFUSCATE_COOKIES: set[str] =  {"session"}
"""Request cookie keys to obfuscate."""
LOG_OBFUSCATE_HEADERS: set[str] = {"Authorization", "X-API-KEY"}
"""Request header keys to obfuscate."""
LOG_JOB_FIELDS: list[str] = [
    "function",
    "kwargs",
    "key",
    "scheduled",
    "attempts",
    "completed",
    "queued",
    "started",
    "result",
    "error",
]
"""Attributes of the SAQ.

[`Job`](https://github.com/tobymao/saq/blob/master/saq/job.py) to be
logged.
"""
LOG_REQUEST_FIELDS: list[RequestExtractorField] = [
        "path",
        "method",
        "headers",
        "cookies",
        "query",
        "path_params",
        "body",
]
"""Attributes of the [Request][litestar.connection.request.Request] to be
logged."""
LOG_RESPONSE_FIELDS: list[ResponseExtractorField] = [
    "status_code",
    "cookies",
    "headers",
    "body",
]
"""Attributes of the [Response][litestar.response.Response] to be
logged."""
LOG_WORKER_EVENT: str = "Worker"
"""Log event name for logs from SAQ worker."""
LOG_SAQ_LEVEL: int = 20
"""Level to log SAQ logs."""
LOG_SQLALCHEMY_LEVEL: int = 20
"""Level to log SQLAlchemy logs."""
LOG_UVICORN_ACCESS_LEVEL: int = 20
"""Level to log uvicorn access logs."""
LOG_UVICORN_ERROR_LEVEL: int = 20
"""Level to log uvicorn error logs."""
LOG_GRANIAN_ACCESS_LEVEL: int = 30
"""Level to log uvicorn access logs."""
LOG_GRANIAN_ERROR_LEVEL: int = 20
"""Level to log uvicorn error logs."""


# ----------------------------- REDIS -----------------------------------------

REDIS_URL: str = "redis://localhost:6379/0"
"""A Redis connection URL."""
REDIS_SOCKET_CONNECT_TIMEOUT: int = 5
"""Length of time to wait (in seconds) for a connection to become active."""
REDIS_HEALTH_CHECK_INTERVAL: int = 5
"""Length of time to wait (in seconds) before testing connection health."""
REDIS_SOCKET_KEEPALIVE: bool = True
"""Length of time to wait (in seconds) between keepalive commands."""

# ------------------------------- REDIS -----------------------------------------

SAQ_PROCESSES: int = 1
"""The number of worker processes to start.

Default is set to 1.
"""
SAQ_CONCURRENCY: int = 10
"""The number of concurrent jobs allowed to execute per worker process.

Default is set to 10.
"""
SAQ_WEB_ENABLED: bool = True
"""If true, the worker admin UI is hosted on worker startup."""
SAQ_USE_SERVER_LIFESPAN: bool = True
"""Auto start and stop `saq` processes when starting the Litestar application."""


# --------------------------------- VITE -------------------------------

VITE_DEV_MODE: bool = False
"""Start `vite` development server."""
VITE_USE_SERVER_LIFESPAN: bool = True
"""Auto start and stop `vite` processes when running in development mode.."""
VITE_HOST: str = "0.0.0.0"
"""The host the `vite` process will listen on.  Defaults to `0.0.0.0`"""
VITE_PORT: int = 5173
"""The port to start vite on.  Default to `5173`"""
VITE_HOT_RELOAD: bool = True
"""Start `vite` with HMR enabled."""
VITE_ENABLE_REACT_HELPERS: bool = True
"""Enable React support in HMR."""
VITE_BUNDLE_DIR: Path = BASE_DIR / "web/public"
"""Bundle directory"""
VITE_RESOURCE_DIR: Path = Path("resources")
"""Resource directory"""
VITE_TEMPLATE_DIR: Path = BASE_DIR / "web/templates"
"""Template directory."""
VITE_ASSET_URL: str = "/static/"
"""Base URL for assets"""

