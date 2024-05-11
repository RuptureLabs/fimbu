from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar, overload

from litestar.dto import DataclassDTO, dto_field
from litestar.dto.config import DTOConfig
from litestar.types.protocols import DataclassProtocol
from litestar.contrib.pydantic import PydanticDTO
from fimbu.db import Model
from fimbu.core.types import ModelT

if TYPE_CHECKING:
    from collections.abc import Set as AbstractSet

    from litestar.dto import RenameStrategy

__all__ = ("config", "dto_field", "DTOConfig", "SQLAlchemyDTO", "DataclassDTO")

DTOT = TypeVar("DTOT", bound=DataclassProtocol | Model)
DTOFactoryT = TypeVar("DTOFactoryT", bound=DataclassDTO | PydanticDTO)
DataclassModelT = TypeVar("DataclassModelT", bound=DataclassProtocol)



@overload
def config(
    backend: Literal["pydantic"] = "pydantic",
    exclude: AbstractSet[str] | None = None,
    rename_fields: dict[str, str] | None = None,
    rename_strategy: RenameStrategy | None = None,
    max_nested_depth: int | None = None,
    partial: bool | None = None,
) -> DTOConfig:
    ...


@overload
def config(
    backend: Literal["dataclass"] = "dataclass",
    exclude: AbstractSet[str] | None = None,
    rename_fields: dict[str, str] | None = None,
    rename_strategy: RenameStrategy | None = None,
    max_nested_depth: int | None = None,
    partial: bool | None = None,
) -> DTOConfig:
    ...


def config(
    backend: Literal["dataclass", "pydantic"] = "dataclass",
    exclude: AbstractSet[str] | None = None,
    rename_fields: dict[str, str] | None = None,
    rename_strategy: RenameStrategy | None = None,
    max_nested_depth: int | None = None,
    partial: bool | None = None,
) -> DTOConfig:
    """_summary_

    Returns:
        DTOConfig: Configured DTO class
    """
    default_kwargs = {"rename_strategy": "camel", "max_nested_depth": 2}
    if exclude:
        default_kwargs["exclude"] = exclude
    if rename_fields:
        default_kwargs["rename_fields"] = rename_fields
    if rename_strategy:
        default_kwargs["rename_strategy"] = rename_strategy
    if max_nested_depth:
        default_kwargs["max_nested_depth"] = max_nested_depth
    if partial:
        default_kwargs["partial"] = partial
    return DTOConfig(**default_kwargs)
