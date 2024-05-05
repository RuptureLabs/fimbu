from typing import TypeVar, Protocol, Any, List, runtime_checkable
from litestar import Litestar
from fimbu.db import Model


# Generic Type
T = TypeVar("T")

# Generic model Type
ModelT = TypeVar("ModelT", bound="Model")


@runtime_checkable
class ApplicationType(Protocol):
    """
    Application protocol
    """
    asgi_application : "Litestar" = None
    plugins: List[Any] = []
    middlewares: List[Any] = []
    dependencies: dict[str, Any] = {}
