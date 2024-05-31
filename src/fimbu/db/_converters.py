from __future__ import annotations

from functools import partial
from pathlib import Path, PurePath
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    List,
    Sequence,
    cast, overload
)
from uuid import UUID

from litestar.pagination import OffsetPagination
from fimbu.db.filters import FilterTypes, LimitOffset
from fimbu.core.types import ModelT, ModelDTOT, RowMappingT


if TYPE_CHECKING:
    from sqlalchemy import ColumnElement
    from collections.abc import Sequence

    from sqlalchemy import RowMapping
    from sqlalchemy.sql import ColumnElement

    from fimbu.db.filters import OffsetPagination, FilterTypes
    from fimbu.core.types import T, ModelDTOT, RowMappingT, ModelT

try:
    from msgspec import Struct, convert
except ImportError:  # pragma: nocover

    class Struct:  # type: ignore[no-redef]
        """Placeholder Implementation"""

    def convert(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef] # noqa: ARG001
        """Placeholder implementation"""
        return {}


try:
    from pydantic import BaseModel
    from pydantic.type_adapter import TypeAdapter
except ImportError:  # pragma: nocover

    class BaseModel:  # type: ignore[no-redef]
        """Placeholder Implementation"""

    class TypeAdapter:  # type: ignore[no-redef]
        """Placeholder Implementation"""


EMPTY_FILTER: list[FilterTypes] = []


def _default_deserializer(
    target_type: Any,
    value: Any,
    type_decoders: Sequence[tuple[Callable[[Any], bool], Callable[[Any, Any], Any]]] | None = None,
) -> Any:  # pragma: no cover
    """Transform values non-natively supported by ``msgspec``

    Args:
        target_type: Encountered type
        value: Value to coerce
        type_decoders: Optional sequence of type decoders

    Returns:
        A ``msgspec``-supported type
    """

    if isinstance(value, target_type):
        return value

    if type_decoders:
        for predicate, decoder in type_decoders:
            if predicate(target_type):
                return decoder(target_type, value)

    if issubclass(target_type, (Path, PurePath, UUID)):
        return target_type(value)

    msg = f"Unsupported type: {type(value)!r}"
    raise TypeError(msg)


def _find_filter(
    filter_type: type[T],
    *filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes],
) -> T | None:
    """Get the filter specified by filter type from the filters.

    Args:
        filter_type: The type of filter to find.
        *filters: filter types to apply to the query

    Returns:
        The match filter instance or None
    """
    return next(
        (cast("T | None", filter_) for filter_ in filters if isinstance(filter_, filter_type)),
        None,
    )


def to_schema(
    data: ModelT | Sequence[ModelT] | Sequence[RowMappingT] | RowMappingT,
    total: int | None = None,
    filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
    schema_type: type[ModelT | ModelDTOT | RowMappingT] | None = None,
) -> (
    ModelT | OffsetPagination[ModelT] | ModelDTOT | OffsetPagination[ModelDTOT] 
    | RowMappingT | OffsetPagination[RowMappingT] 
):
    if schema_type is not None and issubclass(schema_type, Struct):
        if not isinstance(data, Sequence):
            return convert(  # type: ignore  # noqa: PGH003
                obj=data,
                type=schema_type,
                from_attributes=True,
                dec_hook=partial(
                    _default_deserializer,
                    type_decoders=[
                        (lambda x: x is UUID, lambda t, v: t(v.hex)),
                    ],
                ),
            )
        limit_offset = _find_filter(LimitOffset, *filters)
        total = total or len(data)
        limit_offset = limit_offset if limit_offset is not None else LimitOffset(limit=len(data), offset=0)
        return OffsetPagination[schema_type](  # type: ignore[valid-type]
            items=convert(
                obj=data,
                type=List[schema_type],  # type: ignore[valid-type]
                from_attributes=True,
                dec_hook=partial(
                    _default_deserializer,
                    type_decoders=[
                        (lambda x: x is UUID, lambda t, v: t(v.hex)),
                    ],
                ),
            ),
            limit=limit_offset.limit,
            offset=limit_offset.offset,
            total=total,
        )

    if schema_type is not None and issubclass(schema_type, BaseModel):
        if not isinstance(data, Sequence):
            return TypeAdapter(schema_type).validate_python(data, from_attributes=True)  # type: ignore  # noqa: PGH003
        limit_offset = _find_filter(LimitOffset, *filters)
        total = total if total else len(data)
        limit_offset = limit_offset if limit_offset is not None else LimitOffset(limit=len(data), offset=0)
        return OffsetPagination[schema_type](  # type: ignore[valid-type]
            items=TypeAdapter(List[schema_type]).validate_python(data, from_attributes=True),  # type: ignore[valid-type]
            limit=limit_offset.limit,
            offset=limit_offset.offset,
            total=total,
        )
    if not issubclass(type(data), Sequence):
        return data  # type: ignore[return-value]
    limit_offset = _find_filter(LimitOffset, *filters)
    total = total or len(data)  # type: ignore[arg-type]
    limit_offset = limit_offset if limit_offset is not None else LimitOffset(limit=len(data), offset=0)  # type: ignore[arg-type]
    return OffsetPagination[ModelT](
        items=data,  # type: ignore[arg-type]
        limit=limit_offset.limit,
        offset=limit_offset.offset,
        total=total,
    )




class ResultConverter:
    """Simple mixin to help convert to a paginated response model the results set is a list."""

    @overload
    def to_schema(
        self,
        data: RowMappingT,
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
    ) -> RowMappingT: ...

    @overload
    def to_schema(
        self,
        data: Sequence[RowMappingT],
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
    ) -> OffsetPagination[RowMappingT]: ...

    @overload
    def to_schema(
        self,
        data: RowMapping,
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelDTOT] | None = None,
    ) -> ModelDTOT: ...

    @overload
    def to_schema(
        self,
        data: Sequence[RowMapping],
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelDTOT] | None = None,
    ) -> OffsetPagination[ModelDTOT]: ...

    @overload
    def to_schema(
        self,
        data: ModelT,
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
    ) -> ModelT: ...

    @overload
    def to_schema(
        self,
        data: Sequence[ModelT],
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
    ) -> OffsetPagination[ModelT]: ...

    @overload
    def to_schema(
        self,
        data: ModelT,
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelT] = ...,
    ) -> ModelT: ...

    @overload
    def to_schema(
        self,
        data: Sequence[ModelT],
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelT] = ...,
    ) -> OffsetPagination[ModelT]: ...

    @overload
    def to_schema(
        self,
        data: ModelT,
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelDTOT] | None = None,
    ) -> ModelDTOT: ...

    @overload
    def to_schema(
        self,
        data: Sequence[ModelT],
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelDTOT] | None = None,
    ) -> OffsetPagination[ModelDTOT]: ...

    def to_schema(
        self,
        data: ModelT | Sequence[ModelT] | Sequence[RowMappingT] | RowMappingT,
        total: int | None = None,
        filters: Sequence[FilterTypes | ColumnElement[bool]] | Sequence[FilterTypes] = EMPTY_FILTER,
        schema_type: type[ModelDTOT | ModelT] | None = None,
    ) -> (
        ModelT
        | OffsetPagination[ModelT]
        | ModelDTOT
        | OffsetPagination[ModelDTOT]
        | RowMapping
        | OffsetPagination[RowMappingT]
    ):
        """Convert the object to a response schema.  When `schema_type` is None, the model is returned with no conversion.

        Args:
            data: The return from one of the service calls.
            total: the total number of rows in the data
            schema_type: Collection route filters.
            filters: Collection route filters.

        Returns:
            The list of instances retrieved from the repository.
        """
        return to_schema(data=data, total=total, filters=filters, schema_type=schema_type)
