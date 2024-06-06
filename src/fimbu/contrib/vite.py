from fimbu.conf import settings
from litestar_vite import ViteConfig

from fimbu.core.types import ApplicationType


def install_vite_plugin(app: ApplicationType) -> None:
    vite = ViteConfig(
        bundle_dir=settings.VITE_BUNDLE_DIR,
        resource_dir=settings.VITE_RESOURCE_DIR,
        template_dir=settings.VITE_TEMPLATE_DIR,
        use_server_lifespan=settings.VITE_USE_SERVER_LIFESPAN,
        dev_mode=settings.VITE_DEV_MODE,
        hot_reload=settings.VITE_HOT_RELOAD,
        is_react=settings.VITE_ENABLE_REACT_HELPERS,
        port=settings.VITE_PORT,
        host=settings.VITE_HOST,
    )

    if isinstance(app, ApplicationType):
        app.set_config(
            'plugins',
            [vite]
        )
    else:
        raise TypeError("app must be an instance or Application")
