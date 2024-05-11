from __future__ import annotations

from typing import TypeVar, Protocol, Any, List, runtime_checkable
from sqlalchemy import RowMapping  # noqa: TCH002
from typing_extensions import TypeAlias

from fimbu.db.filters import FilterTypes

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


try:
    from msgspec import Struct
except ImportError:  # pragma: nocover

    class Struct:  # type: ignore[no-redef]
        """Placeholder Implementation"""


try:
    from pydantic import BaseModel
except ImportError:  # pragma: nocover

    class BaseModel:  # type: ignore[no-redef]
        """Placeholder Implementation"""


ModelDictT: TypeAlias = "dict[str, Any] | ModelT"
ModelDictListT: TypeAlias = "list[ModelT | dict[str, Any]] | list[dict[str, Any]]"
FilterTypeT = TypeVar("FilterTypeT", bound=FilterTypes)
ModelDTOT = TypeVar("ModelDTOT", bound="Struct | BaseModel")
RowMappingT = TypeVar("RowMappingT", bound="RowMapping")
