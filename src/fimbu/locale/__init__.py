from .core import Babel, BabelCli, _, BabelPlugin
from .middleware import BabelMiddleware
from .properties import RootConfigs as BabelConfigs

from fimbu.core.types import ApplicationType


__all__ = [
    "Babel",
    "BabelCli",
    "BabelConfigs",
    "_",
    "install_babel_plugin",
    "BabelPlugin",
    "BabelMiddleware",
]


def install_babel_plugin(app : ApplicationType) -> None:
    babel_plugin = BabelPlugin(BabelConfigs.from_settings())
    if isinstance(app, ApplicationType):
        app.set_config(
            'plugins',
            [babel_plugin]
        )
    else:
        raise TypeError("app must be an instance or Application")
