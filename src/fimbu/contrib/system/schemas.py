from dataclasses import dataclass
from typing import Literal

from fimbu.conf import settings
from fimbu import __version__ as current_version

__all__ = ("SystemHealth",)



@dataclass
class SystemHealth:
    database_status: Literal["online", "offline"]
    cache_status: Literal["online", "offline"]
    worker_status: Literal["online", "offline"]
    app: str = settings.APP_NAME
    version: str = current_version
