from __future__ import annotations

from gettext import gettext, translation
from typing import TYPE_CHECKING

from click import Group
from litestar.config.app import AppConfig

from .helpers import check_click_import, check_jinja_import
from .properties import RootConfigs
from .exceptions import BabelProxyError
from ._commands import BabelCli
from contextvars import ContextVar
from litestar.plugins import CLIPluginProtocol, InitPluginProtocol
from litestar.middleware import DefineMiddleware


if TYPE_CHECKING:
    from typing import Callable, Optional
    from litestar.contrib.jinja import JinjaTemplateEngine
    from litestar import Request






class Babel:

    instance: Optional[Babel] = None  # Singleton used by Babel CLI

    def __init__(self, configs: RootConfigs) -> None:
        """
        `Babel` is manager for babel localization
            and i18n tools like gettext, translation, ...

        Args:
            configs (RootConfigs): Babel configs for using.
        """
        self.config: RootConfigs = configs
        self.__locale: str = self.config.BABEL_DEFAULT_LOCALE
        self.__default_locale: str = self.config.BABEL_DEFAULT_LOCALE
        self.__domain: str = self.config.BABEL_DOMAIN.split(".")[0]

    @property
    def domain(self) -> str:
        return self.__domain

    @property
    def default_locale(self) -> str:
        return self.__default_locale

    @property
    def locale(self) -> str:
        return self.__locale

    @locale.setter
    def locale(self, value: str) -> None:
        self.__locale = value

    @property
    def gettext(self) -> Callable[[str], str]:
        if self.default_locale != self.locale:
            gt = translation(
                self.domain,
                self.config.BABEL_TRANSLATION_DIRECTORY,
                [self.locale],
            )
            gt.install()
            return gt.gettext
        return gettext

    def install_jinja(self, engine: JinjaTemplateEngine) -> None:
        """
        `Babel.install_jinja` install gettext to jinja2 environment
            to access `_` in whole
            the jinja templates and let it to pybabel for
            extracting included messages throughout the templates.

        """
        check_jinja_import()
        engine.register_template_callable('_', _)


    def run_cli(self):
        """installs cli's for using pybabel commands easily by specified
        configs from `BabelConfigs`.
        """
        check_click_import()
        babel_cli = BabelCli(self)
        babel_cli.run()


class __LazyText:
    def __init__(self, message) -> None:
        self.message = message

    def __repr__(self) -> str:
        return _(self.message)


def make_gettext(request: Request) -> Callable[[str], str]:
    """translate the message and retrieve message from .PO and .MO depends on
    `Babel.locale` locale.

    Args:
        message (str): message content

    Returns:
        str: transalted message.
    """

    def translate(message: str) -> str:
        # Get Babel instance from request or fallback to the CLI instance (when defined)
        babel = getattr(request.state, "babel", Babel.instance)
        if babel is None:
            raise BabelProxyError(
                "Babel instance is not available in the current request context."
            )

        return babel.gettext(message)

    return translate


_context_var: ContextVar[Callable[[str], str]] = ContextVar("gettext")


def _(message: str) -> str:
    gettext = _context_var.get()
    return gettext(message)


lazy_gettext = __LazyText


class BabelPlugin(InitPluginProtocol, CLIPluginProtocol):
    def __init__(self, babel_configs: RootConfigs):
        self.babel_configs = babel_configs

    def on_app_init(self, app_config: AppConfig) -> AppConfig:
        from fimbu.locale.middleware import BabelMiddleware

        app_config.middleware.append(
            DefineMiddleware(
                BabelMiddleware, 
                configs=self.babel_configs,
                template_engine=app_config.template_config.engine_instance
            )
        )
        return super().on_app_init(app_config)
    
    
    def on_cli_init(self, cli: Group) -> None:
        b_cli = BabelCli(Babel(self.babel_configs)).get_babel_cli()
        cli.add_command(b_cli)
