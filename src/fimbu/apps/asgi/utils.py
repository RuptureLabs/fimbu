from typing import List, Iterable
from pathlib import Path
from litestar.template.config import TemplateConfig
from litestar.static_files.config import StaticFilesConfig
from litestar.plugins import InitPluginProtocol

from fimbu.conf import settings
from fimbu.core.exceptions import ImproperlyConfigured, LoadMiddlewareError
from fimbu.utils.module_loading import import_string



def get_template_config() -> TemplateConfig | None:
    """Get template configuration.

    Returns:
        TemplateConfig | None: Template configuration.

    Raises:
        ImproperlyConfigured: If settings.TEMPLATES is not a TemplateConfig or dict.
    """
    if not settings.TEMPLATES:
        return None

    if isinstance(settings.TEMPLATES, TemplateConfig):
        return settings.TEMPLATES

    if isinstance(settings.TEMPLATES, dict):
        try:
            _dirs = settings.TEMPLATES["DIRS"]
            _engine = settings.TEMPLATES["ENGINE"]
        except LookupError as exc:
            raise ImproperlyConfigured("Unable to find template directory and/or template engine.") from exc
        
        return TemplateConfig(directory=_dirs, engine=_engine)
        
    raise ImproperlyConfigured("settings.TEMPLATES must be a TemplateConfig or dict.")



def _parse_static_config(conf: dict) -> StaticFilesConfig:
    """Parse static files configuration.

    Args:
        conf (dict): Static files configuration.

    Returns:
        StaticFilesConfig: Static files configuration.
    """
    _conf = {}
    _dirs = conf.get("DIRS", None)
    if _dirs is None or not isinstance(_dirs, (list, tuple)) or len(_dirs) < 1:
        raise ImproperlyConfigured("settings.STATIC_FILES.DIRS must be a list and must contain at least one directory.")
    
    _conf["directories"] = _dirs

    _path = conf.get("PATH", None)
    if _path is None or not isinstance(_path, (str, Path)):
        raise ImproperlyConfigured("settings.STATIC_FILES.PATH must be a string or a Path instance.")
    _conf["path"] = _path

    _conf["html_mode"] = True if conf.get("HTML_MODE", None) else False

    _conf["send_as_attachment"] = True if conf.get("AS_ATTACHMENT", None) else False

    _name = conf.get("NAME", None)
    if _name and isinstance(_name, str):
        _conf["name"] = _name

    return StaticFilesConfig(**_conf)


def get_static_file_config() -> List[StaticFilesConfig]:
    """Get static files configuration.

    Returns:
        List[StaticFilesConfig]: Static files configuration.

    Raises:
        ImproperlyConfigured: If settings.STATIC_FILES has a dictionary that is missing the path and/or folders attribute.
    """
    configs = []
    if isinstance(settings.STATIC_FILES, list) or isinstance(settings.STATIC_FILES, tuple):
        for conf in settings.STATIC_FILES:
            if isinstance(conf, dict):
                configs.append(_parse_static_config(conf))
            elif isinstance(conf, StaticFilesConfig):
                configs.append(conf)
            else:
                raise ImproperlyConfigured("settings.STATIC_FILES element must be a dict or StaticFilesConfig.")
        
        return configs
    raise ImproperlyConfigured("settings.STATIC_FILES must be a list or tuple.")



def get_middleware()-> List:
    """Load Middlewares from settings"""
    _mids = []
    if hasattr(settings, 'MIDDLEWARE'):
        mids:Iterable = settings.MIDDLEWARE
        for mid in mids:
            if isinstance(mid, str):
                try:
                    _mid = import_string(mid)
                    _mids.append(_mid)
                except Exception as ex:
                    raise LoadMiddlewareError(f"failed to load {mid}, {ex}") from ex
            else:
                raise ImproperlyConfigured(f"middleware in settings.MIDDLEWARE must compatible string for import, {mid} is not a string")
    return _mids

def get_auth_plugin():
    """Load auth plugin from settings"""
    if hasattr(settings, 'AUTH_PLUGIN'):
        if isinstance(settings.AUTH_PLUGIN, InitPluginProtocol):
            return import_string(settings.AUTH_PLUGIN)
            
        elif isinstance(settings.AUTH_PLUGIN, str):
            try:
                auth = import_string(settings.AUTH_PLUGIN)
                if not isinstance(auth, InitPluginProtocol):
                    raise LoadMiddlewareError(f"{settings.AUTH_PLUGIN} is not an InitPluginProtocol")
                return auth
            except Exception as ex:
                raise LoadMiddlewareError(f"failed to load {settings.AUTH_PLUGIN}, {ex}") from ex
        else:
            raise ImproperlyConfigured(f"AUTH_PLUGIN in settings must be a string or InitPluginProtocol, {settings.AUTH_PLUGIN} is not a string")
        
    elif hasattr(settings, 'USER_MODEL'):
        from fimbu.contrib.auth.main import AuthPlugin, AuthConfig

        try:
            user_model = import_string(settings.USER_MODEL)

            if hasattr(settings, 'AUTH_BACKEND'):
                auth_backend = import_string(settings.AUTH_BACKEND)
            else:
                from litestar.security.session_auth import SessionAuth
                auth_backend = SessionAuth
            
            if hasattr(settings, 'USER_READ_DTO'):
                user_read_dto = import_string(settings.USER_READ_DTO)
            else:
                from fimbu.contrib.auth.dtos import UserReadDTO
                user_read_dto = UserReadDTO

            if hasattr(settings, 'USER_REGISTRATION_DTO'):
                user_registration_dto = import_string(settings.USER_REGISTRATION_DTO)
            else:
                from fimbu.contrib.auth.dtos import UserRegistrationDTO
                user_registration_dto = UserRegistrationDTO

            if hasattr(settings, 'USER_UPDATE_DTO'):
                user_update_dto = import_string(settings.USER_UPDATE_DTO)
            else:
                from fimbu.contrib.auth.dtos import UserUpdateDTO
                user_update_dto = UserUpdateDTO

            if hasattr(settings, 'USER_SERVICE'):
                user_service = import_string(settings.USER_SERVICE)
            else:
                from fimbu.contrib.auth.service import UserService
                user_service = UserService

            if hasattr(settings, 'AUTH_HANDLER_CONFIG'):
                auth_handler_config = import_string(settings.AUTH_HANDLER_CONFIG)
            else:
                from fimbu.contrib.auth.config import AuthHandlerConfig
                auth_handler_config = AuthHandlerConfig()

            if hasattr(settings, 'REGISTER_HANDLER_CONFIG'):
                register_handler_config = import_string(settings.REGISTER_HANDLER_CONFIG)
            else:
                from fimbu.contrib.auth.config import RegisterHandlerConfig
                register_handler_config = RegisterHandlerConfig()

            if hasattr(settings, 'VERIFICATION_HANDLER_CONFIG'):
                verification_handler_config = import_string(settings.VERIFICATION_HANDLER_CONFIG)
            else:
                from fimbu.contrib.auth.config import VerificationHandlerConfig
                verification_handler_config = VerificationHandlerConfig()


            return AuthPlugin(
                config=AuthConfig(
                    auth_backend_class=auth_backend,
                    secret=settings.SECRET,
                    user_model=user_model,
                    user_read_dto=user_read_dto,
                    user_registration_dto=user_registration_dto,
                    user_update_dto=user_update_dto,
                    user_service_class=user_service,
                    auth_handler_config=auth_handler_config,
                    register_handler_config=register_handler_config,
                    verification_handler_config=verification_handler_config,
                )
            )
        except Exception as ex:
            raise LoadMiddlewareError(f"failed to load AUTH_PLUGIN from settings, {ex}") from ex
    
