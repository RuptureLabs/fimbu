from typing import Literal, Type
from pathlib import Path
from litestar.contrib.jinja import JinjaTemplateEngine
from litestar.static_files.config import StaticFilesConfig
from litestar.middleware.compression import CompressionMiddleware
from litestar.types import Scopes, Method

BASE_DIR = Path.cwd()


SECRET = 'fimbu_secret_key'

DEBUG = True

INSTALLED_APPS = []

MIDDLEWARE = []

MIDDLEWARE_FROM_FACTORY_BEFORE = False

ROOT_URLCONF = 'api.urls'


ASGI_APPLICATION = 'fimbu.apps.main:app'


DATABASES = {
    "engine": "sqlite",
    "database": "database.db",
    "host": "127.0.0.1",
    "password": "stone#",
    "port": 5432,
    "user": "eddy",
}


# Templates

TEMPLATES = {
    'DIRS' : ['templates'],
    'ENGINE' : JinjaTemplateEngine,
}

# TEMPLATES = TemplateConfig(
#         directory=Path("templates"),
#         engine=JinjaTemplateEngine,
#     )


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

# Internationalization
# https://docs.djangoproject.com/en/{{ docs_version }}/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


APP_MIGRATIONS_FOLDER = 'migrations'

MIGRATIONS_PER_APP = False # experimental

MIGRATIONS_LOCATION = BASE_DIR / APP_MIGRATIONS_FOLDER



TEST_RUNNER = 'oya.test.runner.DiscoverRunner'

########### ------------------------------ UVICORN ---------------------------------- ##########

UVICORN_PORT = 8080
UVICORN_LOG_LEVEL = 'info'



########## ------------------------------- OYA ------------------------------------ ##########
OYA_VERSION = '0.0.1'
APP_NAME = "{{ camel_case_name }}"


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



DEBUG = False
INSTALLED_APPS = ()

# Default charset to use for all HttpResponse objects, if a MIME type isn't
# manually specified. It's used to construct the Content-Type header.
DEFAULT_CHARSET = "utf-8"

# Email address that error messages come from.
SERVER_EMAIL = "root@localhost"

# Database connection info. If left empty, will default to the dummy backend.
DATABASES = {}

# Classes used to implement DB routing behavior.
DATABASE_ROUTERS = []

# The email backend to use. For possible shortcuts see django.core.mail.
# The default is to use the SMTP backend.
# Third-party backends can be specified by providing a Python path
# to a module that defines an EmailBackend class.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# Host for sending email.
EMAIL_HOST = "localhost"

# Port for sending email.
EMAIL_PORT = 25

# Whether to send SMTP 'Date' header in the local time zone or in UTC.
EMAIL_USE_LOCALTIME = False

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_SSL_CERTFILE = None
EMAIL_SSL_KEYFILE = None
EMAIL_TIMEOUT = None

# List of strings representing installed apps.
INSTALLED_APPS = []

TEMPLATES = []

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Default form rendering class.
FORM_RENDERER = "django.forms.renderers.DjangoTemplates"

# Default email address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = "webmaster@localhost"

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = "[Oya] "
