from typing import Literal, Type
from pathlib import Path
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files.config import StaticFilesConfig
from litestar.middleware.compression import CompressionMiddleware
from litestar.types import Scopes, Method


########## ------------------------------- FIMBU - PROJECT --------------------------------- ##########

BASE_DIR = Path.cwd()
SECRET = 'fimbu_secret_key'
DEBUG = True
OYA_VERSION = '0.0.1'
APP_NAME = "fimbu"
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

INSTALLED_APPS = []

MIDDLEWARE = []

MIDDLEWARE_FROM_FACTORY_BEFORE = False

ASGI_APPLICATION = 'fimbu.apps.main:app'


DATABASES = [
    {
    "primary": True,
    "engine": "sqlite",
    "database": "database.db",
    },
]


# Templates

TEMPLATES = {
    'DIRS' : ['templates'],
    'ENGINE' : JinjaTemplateEngine,
}


# Static files

STATIC_FILES = [
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


APP_MIGRATIONS_FOLDER = 'migrations'

MIGRATIONS_LOCATION = BASE_DIR / APP_MIGRATIONS_FOLDER


####### -------------------------------- ALLOWED HOSTS CONFIG --------------------- #########

ALLOWED_HOSTS: list[str] = ['127.0.0.1']
EXCLUDE_HOSTS: str | list[str] | None = None  # exclude parameter from Litestar's AllowedHostsConfig
ALLOWED_HOSTS_EXCLUDE_OPT_KEY: str | None = None # exclude_opt_key parameter from Litestar's AllowedHostsConfig
ALLOWED_HOSTS_SCOPES: Type[Scopes] | None = None
WWW_REDIRECT: bool = True


####### -------------------------------- CORS CONFIG ------------------------------ ##########

ALLOW_ORIGINS: list[str] = []
ALLOW_METHODS: list[str] = ['*']
ALLOW_HEADERS: list[str] = []
ALLOW_CREDENTIALS: bool = False
ALLOW_ORIGIN_REGEX: str | None = None
EXPOSE_HEADERS: list[str] = []
CORS_MAX_AGE: int = 600


##### -------------------------------- COMPRESSION CONFIG ------------------------- ###########

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

AUTH_PLUGIN = 'fimbu.contrib.auth.plugins.BearerAuthentication'
AUTH_BACKEND = 'fimbu.contrib.auth.backends.AuthenticationBackend'
USER_MODEL = 'fimbu.contrib.auth.models.User'
USER_READ_DTO = 'fimbu.contrib.auth.dtos.UserReadDTO'
USER_REGISTRATION_DTO = 'fimbu.contrib.auth.dtos.UserRegistrationDTO'
USER_UPDATE_DTO = 'fimbu.contrib.auth.dtos.UserUpdateDTO'
USER_SERVICE = 'fimbu.contrib.auth.service.UserService'
AUTH_HANDLER_CONFIG = 'fimbu.contrib.auth.configs.AuthHandlerConfig'
REGISTRATION_HANDLER_CONFIG = 'fimbu.contrib.auth.configs.RegistrationHandlerConfig'
VERIFICATION_HANDLER_CONFIG = 'fimbu.contrib.auth.configs.VerificationHandlerConfig'
