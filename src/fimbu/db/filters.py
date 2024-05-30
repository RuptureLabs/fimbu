"""Collection filter datastructures."""
from __future__ import annotations

from abc import abstractmethod
from collections import abc  # noqa: TCH003
from dataclasses import dataclass
from datetime import datetime  # noqa: TCH003
from typing import TYPE_CHECKING, Any, Generic, Literal, TypeVar

from fimbu.db.exceptions import RepositoryError
from fimbu.db.utils import get_instrumented_attr
from sqlalchemy import and_, or_, false


if TYPE_CHECKING:
    from typing_extensions import TypeAlias
    from sqlalchemy import ColumnElement
    from sqlalchemy.orm import InstrumentedAttribute
    from edgy import QuerySet
    from fimbu.core.types import ModelT

T = TypeVar("T")

__all__ = (
    "BeforeAfter",
    "CollectionFilter",
    "FilterTypes",
    "LimitOffset",
    "OrderBy",
    "SearchFilter",
    "NotInCollectionFilter",
    "OnBeforeAfter",
    "NotInSearchFilter",
)


FilterTypes: TypeAlias = "BoolFilter | AndFilter | BeforeAfter | OnBeforeAfter | CollectionFilter[Any] | LimitOffset | OrderBy | SearchFilter | NotInCollectionFilter[Any] | NotInSearchFilter"
"""Aggregate type alias of the types supported for collection filtering."""


@dataclass(kw_only=True)
class BoolFilter:
    """Data required to construct a ``WHERE ... AND ...`` or ``WHERE ... OR ...`` clause."""
    _expression: ColumnElement[bool] | None = None
    """Boolean expression to apply to the query."""

    queryset: QuerySet[ModelT] | None = None

    left_op: FilterTypes
    """left operand."""
    right_op: FilterTypes
    """right operand."""

    @abstractmethod
    def _process_expression(self):
        ...

    def get_expression(self, queryset: QuerySet[ModelT]) -> None:
        self.queryset = queryset
        
        if self._expression is None:
            self._expression = self._process_expression()
        return self._expression
    

    def _apply_filters(self, filter_: FilterTypes):
        instr_attr = get_instrumented_attr(self.queryset.model_class, filter_.field_name)
        expr: ColumnElement[bool] = false() # returns nothing
        
        if isinstance(filter_, (LimitOffset,)):
            raise TypeError("Cannot use pagination filter with BoolFilter.")

        elif isinstance(filter_, (BeforeAfter,)):
            expr = self._filter_on_datetime_field(
                field_name=instr_attr,
                before=filter_.before,
                after=filter_.after,
            )

        elif isinstance(filter_, (OnBeforeAfter,)):
            expr = self._filter_on_datetime_field(
                field_name=instr_attr,
                on_or_before=filter_.on_or_before,
                on_or_after=filter_.on_or_after,
            )

        elif isinstance(filter_, (NotInCollectionFilter,)):
            expr = self._filter_not_in_collection(
                instr_attr,
                filter_.values,
            )

        elif isinstance(filter_, (CollectionFilter,)):
            expr = self._filter_in_collection(
                instr_attr, 
                filter_.values,
            )

        elif isinstance(filter_, (OrderBy,)):
            raise TypeError("Cannot use OrderBy filter with BoolFilter.")

        elif isinstance(filter_, (SearchFilter,)):
            expr = self._filter_by_like(
                instr_attr,
                value=filter_.value,
                ignore_case=bool(filter_.ignore_case),
            )

        elif isinstance(filter_, (BetweenFilter,)):
            expr = self._filter_between(
                instr_attr,
                start=filter_.start,
                end=filter_.end,
            )

        elif isinstance(filter_, (NotInSearchFilter,)):
            expr = self._filter_by_not_like(
                instr_attr,
                value=filter_.value,
                ignore_case=bool(filter_.ignore_case),
            )
        else:
            msg = f"Unexpected filter: {filter_}"  # type: ignore[unreachable]
            raise RepositoryError(msg)
        
        return expr


    def _filter_between(
        self,
        field_name: InstrumentedAttribute,
        start: datetime | int,
        end: datetime | int,
    ) -> ColumnElement[bool]:
        return field_name.between(start, end)

    def _filter_in_collection(
        self,
        field_name: str | InstrumentedAttribute,
        values: abc.Collection[Any],
    ) -> ColumnElement[bool]:
        if not values:
            return or_(false())
        return field_name.in_(values)


    def _filter_not_in_collection(
        self,
        field_name: InstrumentedAttribute,
        values: abc.Collection[Any],
    ) -> ColumnElement[bool]:
        if not values:
            return or_(false())
        return field_name.notin_(values)


    def _filter_on_datetime_field(
        self,
        field_name: str,
        before: datetime | None = None,
        after: datetime | None = None,
        on_or_before: datetime | None = None,
        on_or_after: datetime | None = None,
    ) -> ColumnElement[bool]:
        exp = None
        if before is not None:
            exp = field_name < before
        if after is not None:
            exp = field_name > after if exp is None else exp & (field_name > after)
        if on_or_before is not None:
            exp = field_name <= on_or_before if exp is None else exp & (field_name <= on_or_before)
        if on_or_after is not None:
            exp = field_name >= on_or_after if exp is None else exp & (field_name >= on_or_after)
        return exp


    def _filter_by_like(
        self,
        field_name: InstrumentedAttribute,
        value: str,
        ignore_case: bool,
    ) -> ColumnElement:
        return field_name.ilike(value) if ignore_case else field_name.like(value)


    def _filter_by_not_like(
        self,
        field_name: InstrumentedAttribute,
        value: str,
        ignore_case: bool,
    ) -> ColumnElement:
        return field_name.notilike(value) if ignore_case else field_name.notilike(value)


@dataclass(kw_only=True)
class AndFilter(BoolFilter):
    """Data required to construct a ``WHERE ... AND ...`` clause."""
    _expression: ColumnElement[bool] | None = None
    """Boolean expression to apply to the query."""

    def _process_expression(self) -> ColumnElement[bool]:
        return and_(self._apply_filters(self.left_op), self._apply_filters(self.right_op))


@dataclass(kw_only=True)
class OrFilter(BoolFilter):
    """Data required to construct a ``WHERE ... OR ...`` clause."""
    _expression: ColumnElement[bool] | None = None
    """Boolean expression to apply to the query."""

    def _process_expression(self) -> ColumnElement[bool]:
        return or_(self._apply_filters(self.left_op), self._apply_filters(self.right_op))



@dataclass
class BeforeAfter:
    """Data required to filter a query on a ``datetime`` column."""

    field_name: str
    """Name of the model attribute to filter on."""
    before: datetime | None
    """Filter results where field earlier than this."""
    after: datetime | None
    """Filter results where field later than this."""


@dataclass
class OnBeforeAfter:
    """Data required to filter a query on a ``datetime`` column."""

    field_name: str
    """Name of the model attribute to filter on."""
    on_or_before: datetime | None
    """Filter results where field is on or earlier than this."""
    on_or_after: datetime | None
    """Filter results where field on or later than this."""


@dataclass
class CollectionFilter(Generic[T]):
    """Data required to construct a ``WHERE ... IN (...)`` clause."""

    field_name: str
    """Name of the model attribute to filter on."""
    values: abc.Collection[T] | None
    """Values for ``IN`` clause.

    An empty list will return an empty result set, however, if ``None``, the filter is not applied to the query, and all rows are returned. """


@dataclass
class NotInCollectionFilter(Generic[T]):
    """Data required to construct a ``WHERE ... NOT IN (...)`` clause."""

    field_name: str
    """Name of the model attribute to filter on."""
    values: abc.Collection[T] | None
    """Values for ``NOT IN`` clause.

    An empty list or ``None`` will return all rows."""


@dataclass
class LimitOffset:
    """Data required to add limit/offset filtering to a query."""

    limit: int
    """Value for ``LIMIT`` clause of query."""
    offset: int
    """Value for ``OFFSET`` clause of query."""


@dataclass
class OrderBy:
    """Data required to construct a ``ORDER BY ...`` clause."""

    field_name: str
    """Name of the model attribute to sort on."""
    sort_order: Literal["asc", "desc"] = "asc"
    """Sort ascending or descending"""


@dataclass
class BetweenFilter:
    """Data required to construct a ``WHERE field_name BETWEEN :start AND :end`` clause."""

    field_name: str
    """Name of the model attribute to sort on."""
    start: datetime | int
    """Start of the range."""
    end: datetime | int

@dataclass
class SearchFilter:
    """Data required to construct a ``WHERE field_name LIKE '%' || :value || '%'`` clause."""

    field_name: str
    """Name of the model attribute to sort on."""
    value: str
    """Values for ``LIKE`` clause."""
    ignore_case: bool | None = False
    """Should the search be case insensitive."""


@dataclass
class NotInSearchFilter:
    """Data required to construct a ``WHERE field_name NOT LIKE '%' || :value || '%'`` clause."""

    field_name: str
    """Name of the model attribute to search on."""
    value: str
    """Values for ``NOT LIKE`` clause."""
    ignore_case: bool | None = False
    """Should the search be case insensitive."""


@dataclass
class OffsetPagination(Generic[T]):
    """Container for data returned using limit/offset pagination."""

    __slots__ = ("items", "limit", "offset", "total")

    items: list[T]
    """List of data being sent as part of the response."""
    limit: int
    """Maximal number of items to send."""
    offset: int
    """Offset from the beginning of the query.

    Identical to an index.
    """
    total: int
    """Total number of items."""
