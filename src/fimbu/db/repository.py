from __future__ import annotations

import abc
from typing import Any, Generic, Collection
import string
import random
from datetime import datetime
from uuid import UUID
from edgy import ObjectNotFound, QuerySet, or_
from litestar.repository.abc import AbstractAsyncRepository
from sqlalchemy import text
from fimbu.core.types import ModelT, T


from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement

from fimbu.utils.text import slugify
from fimbu.db.exceptions import RepositoryError
from fimbu.db.filters import (
    BeforeAfter,
    CollectionFilter,
    FilterTypes,
    LimitOffset,
    NotInCollectionFilter,
    NotInSearchFilter,
    OnBeforeAfter,
    OrderBy,
    SearchFilter,
    AndFilter,
    OrFilter,
)



__all__ = [
    "AsyncRepository",
    "FilterableRepository",
]



class FilterableRepository(Generic[ModelT]):
    model_type: type[ModelT]

    def _apply_limit_offset_pagination(
        self,
        limit: int,
        offset: int,
        queryset: QuerySet[ModelT],
    ) -> QuerySet[ModelT]:
        return queryset.limit(limit).offset(offset)

    def _apply_filters(
        self,
        *filters: FilterTypes | ColumnElement[bool], # type: ignore
        apply_pagination: bool = True,
        queryset: QuerySet[ModelT],
    ) -> QuerySet[ModelT]:
        """Apply filters to a select statement.

        Args:
            *filters: filter types to apply to the query
            apply_pagination: applies pagination filters if true
            queryset: chained queryset to apply filters

        Keyword Args:
            select: select to apply filters against

        Returns:
            The Queryset with filters applied.
        """

        order_by_filters: list[OrderBy] = []
        pagination_filter: LimitOffset = None

        for filter_ in filters:
            if isinstance(filter_, (LimitOffset,)):
                if apply_pagination:
                    pagination_filters = filter_

            elif isinstance(filter_, (BeforeAfter,)):
                queryset = self._filter_on_datetime_field(
                    field_name=filter_.field_name,
                    before=filter_.before,
                    after=filter_.after,
                    queryset=queryset,
                )
            elif isinstance(filter_, (OnBeforeAfter,)):
                queryset = self._filter_on_datetime_field(
                    field_name=filter_.field_name,
                    on_or_before=filter_.on_or_before,
                    on_or_after=filter_.on_or_after,
                    queryset=queryset,
                )

            elif isinstance(filter_, (NotInCollectionFilter,)):
                if filter_.values is not None:
                    queryset = self._filter_not_in_collection(
                        filter_.field_name,
                        filter_.values,
                        queryset=queryset,
                    )

            elif isinstance(filter_, (CollectionFilter,)):
                if filter_.values is not None:
                    queryset = self._filter_in_collection(filter_.field_name, filter_.values, queryset=queryset)

            elif isinstance(filter_, (OrderBy,)):
                order_by_filters.append(filter_)

            elif isinstance(filter_, (SearchFilter,)):
                queryset = self._filter_by_like(
                    queryset,
                    filter_.field_name,
                    value=filter_.value,
                    ignore_case=bool(filter_.ignore_case),
                )
            elif isinstance(filter_, (NotInSearchFilter,)):
                queryset = self._filter_by_not_like(
                    queryset,
                    filter_.field_name,
                    value=filter_.value,
                    ignore_case=bool(filter_.ignore_case),
                )

            elif isinstance(filter_, (AndFilter, OrFilter)):
                queryset = queryset.filter(filter_._expression)

            else:
                msg = f"Unexpected filter: {filter_}"  # type: ignore[unreachable]
                raise RepositoryError(msg)
            

        if order_by_filters:
            queryset._order_by
            fieldnames = [f.field_name if f.sort_order == 'asc' else f"-{f.field_name}" for f in order_by_filters]
            queryset = self._order_by(queryset, fieldnames)

        if pagination_filters:
            if not queryset._order_by:
                pass # TODO: LOG Warning

            queryset = self._apply_limit_offset_pagination(
                pagination_filter.limit, 
                pagination_filter.offset,
                queryset
            )

        return queryset

    def _filter_in_collection(
        self,
        field_name: str | InstrumentedAttribute,
        values: abc.Collection[Any],
        queryset: QuerySet[ModelT],
    ) -> QuerySet[ModelT]:
        if not values:
            return queryset.filter(or_()) # returns nothing
        return queryset.filter(**{f'{field_name}__in': values})

    def _filter_not_in_collection(
        self,
        field_name: str,
        values: abc.Collection[Any],
        queryset: QuerySet[ModelT],
    ) -> QuerySet[ModelT]:
        if not values:
            return queryset.filter(or_()) # returns nothing
        return queryset.exclude(**{f'{field_name}__in': values})

    def _filter_on_datetime_field(
        self,
        field_name: str,
        queryset: QuerySet[ModelT] | None = None,
        before: datetime | None = None,
        after: datetime | None = None,
        on_or_before: datetime | None = None,
        on_or_after: datetime | None = None,
    ) -> QuerySet[ModelT]:
        lookup = {}
        if before is not None:
            lookup[f'{field_name}__lt'] = before
        if after is not None:
            lookup[f'{field_name}__gt'] = after
        if on_or_before is not None:
            lookup[f'{field_name}__lte'] = on_or_before
        if on_or_after is not None:
            lookup[f'{field_name}__gte'] = on_or_after
        return queryset.filter(**lookup)

    def _filter_by_like(
        self,
        queryset: QuerySet[ModelT],
        field_name: str,
        value: str,
        ignore_case: bool,
    ) -> QuerySet[ModelT]:
        lookup = f'{field_name}__icontains' if ignore_case else f'{field_name}__contains'
        return queryset.filter(**{lookup: value})

    def _filter_by_not_like(
        self,
        queryset: QuerySet[ModelT],
        field_name: str,
        value: str,
        ignore_case: bool,
    ) -> QuerySet[ModelT]:
        lookup = f'{field_name}__icontains' if ignore_case else f'{field_name}__contains'
        return queryset.exclude(**{lookup: value})

    def _order_by(
        self,
        queryset: QuerySet[ModelT],
        field_names: str | list[str]
    ) -> QuerySet[ModelT]:
        field_names = field_names if isinstance(field_names, list) else [field_names]
        return queryset.order_by(*field_names)



class AsyncRepository(AbstractAsyncRepository[ModelT], FilterableRepository[ModelT]):
    """The base repository class."""

    model_type: type[ModelT]

    def __init__(self, model_type: type[ModelT], **kwargs: Any) -> None:
        """Repository constructors accept arbitrary kwargs."""
        self.model_type = model_type
        self.id_attribute = model_type.pkname
        super().__init__(**kwargs)


    async def add(self, data: ModelT) -> ModelT:
        """Add ``data`` to the collection."""
        return await data.save()
    

    async def add_many(self, data: list[ModelT]) -> list[ModelT]:
        """Add multiple ``data`` to the collection."""
        return await self.model_type.query.bulk_create(data)
    

    async def count(self, *filters: FilterTypes, **kwargs: Any) -> int: # type: ignore
        """Get the count of records returned by a query.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            The count of instances
        """
        queryset = self._apply_filters(filters, apply_pagination=False, queryset=self.model_type.query)
        return await queryset.filter(**kwargs).count()
    

    async def delete(self, item_id: Any) -> ModelT:
        """Delete instance identified by ``item_id``.

        Args:
            item_id: Identifier of instance to be deleted.

        Returns:
            The deleted instance.

        Raises:
            ObjectNotFound: If no instance found identified by ``item_id``.
        """
        instance: ModelT = await self.model_type.query.get(**{self.id_attribute: item_id})
        await instance.delete()
        return instance


    async def delete_many(self, item_ids: list[Any]) -> list[ModelT]:
        """Delete multiple instances identified by list of IDs ``item_ids``.

        Args:
            item_ids: list of Identifiers to be deleted.

        Returns:
            The deleted instances.
        """
        instances: list[ModelT] = await self.model_type.query.filter(**{f"{self.id_attribute}__in": item_ids})
        await self.model_type.query.filter(**{f"{self.id_attribute}__in": item_ids}).delete()
        return instances


    async def exists(self, *filters: Any, **kwargs: Any) -> bool:
        """Return true if the object specified by ``kwargs`` exists.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Identifier of the instance to be retrieved.

        Returns:
            True if the instance was found.  False if not found.

        """
        queryset = self._apply_filters(filters, apply_pagination=False, queryset=self.model_type.query)
        return await queryset.exists(**kwargs)


    async def get(self, item_id: Any, **kwargs: Any) -> ModelT:
        """Get instance identified by ``item_id``.

        Args:
            item_id: Identifier of the instance to be retrieved.
            **kwargs: Additional arguments

        Returns:
            The retrieved instance.

        Raises:
            ObjectNotFound: If no instance found identified by ``item_id``.
            MultipleObjectsReturned: If multiple instances found identified by ``item_id``.
        """
        kwargs[self.id_attribute] = item_id
        return await self.model_type.query.get(**kwargs)


    async def get_one(self, **kwargs: Any) -> ModelT:
        """Get an instance specified by the ``kwargs`` filters if it exists.

        Args:
            **kwargs: Instance attribute value filters.

        Returns:
            The retrieved instance.

        Raises:
            ObjectNotFound: If no instance found identified by ``kwargs``.
            MultipleObjectsReturned: If multiple instances found identified by ``kwargs``.
        """
        return await self.model_type.query.get(**kwargs)


    async def get_or_create(self, **kwargs: Any) -> tuple[ModelT, bool]:
        """Get an instance specified by the ``kwargs`` filters if it exists or create it.

        Args:
            **kwargs: Instance attribute value filters. kwargs must inlcude the defaults map.

        Returns:
            A tuple that includes the retrieved or created instance, and a boolean on whether the record was created or not
        """
        return await self.model_type.query.get_or_create(**kwargs)
    

    async def get_one_or_none(self, **kwargs: Any) -> ModelT | None:
        """Get an instance if it exists or None.

        Args:
            **kwargs: Instance attribute value filters.

        Returns:
            The retrieved instance or None.
        """
        return await self.model_type.query.filter(**kwargs).first()


    async def update_instance(self, instance: ModelT | UUID, **kwargs: Any) -> ModelT:
        """Update instance with the attribute values present on ``kwargs``.

        Args:
            instance: An instance that should have a value for :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` that exists in the
                collection.

        Returns:
            The updated instance.
        """
        if isinstance(instance, UUID):
            instance = await self.model_type.query.get(id=instance)
        
        for key, value in kwargs.items():
            setattr(instance, key, value)

        await instance.save()
        return instance
    

    async def update(self, **kwargs: Any) -> None:
        """Update instance with the attribute values present on ``kwargs``.

        Args:
            kwargs: An instance that should have a value for :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` that exists in the
                collection.

        Returns:
            None.

        Raises:
            ObjectNotFound: If no instance found with same identifier as ``kwargs``.
        """
        if not self.id_attribute in kwargs:
            raise ValueError(f"Missing {self.id_attribute} in kwargs for update")
        
        pk = kwargs.pop(self.id_attribute)
        return await self.model_type.query.filter(**{self.id_attribute: pk}).update(**kwargs)
    

    async def update_many(self, data: list[ModelT]) -> None:
        """Update multiple instances with the attribute values present on instances in ``data``.

        Args:
            data: A list of instance that should have a value for :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` that exists in the
                collection.

        Returns:
            a list of the updated instances.

        Raises:
            ObjectNotFound: If no instance found with same identifier as ``data``.
        """
        return await self.model_type.query.bulk_update(data)
    

    async def upsert(self, **kwargs: Any) -> tuple[ModelT, bool]:
        """Update or create instance.

        Updates instance with the attribute values present on ``data``, or creates a new instance if
        one doesn't exist.

        Args:
            data: Instance to update existing, or be created. Identifier used to determine if an
                existing instance exists is the value of an attribute on ``data`` named as value of
                :attr:`id_attribute <AbstractAsyncRepository.id_attribute>`.

        Returns:
            The updated or created instance.

        Raises:
            ObjectNotFound: If no instance found with same identifier as ``data``.
            DuplicatedRecordError: If an instance already exists with same identifier as ``data`` on <AbstractAsyncRepository.id_attribute>.
        """
        return await self.model_type.query.update_or_create(kwargs)
    

    async def upsert_many(self, data: list[ModelT]) -> list[ModelT]:
        """Update or create multiple instances.

        Update instances with the attribute values present on ``data``, or create a new instance if
        one doesn't exist.

        Args:
            data: Instances to update or created. Identifier used to determine if an
                existing instance exists is the value of an attribute on ``data`` named as value of
                :attr:`id_attribute <AbstractAsyncRepository.id_attribute>`.

        Returns:
            The updated or created instances.

        Raises:
            NotFoundError: If no instance found with same identifier as ``data``.
        """
        raise NotImplementedError("Upsert many is not implemented")


    async def list_and_count(self, *filters: FilterTypes, **kwargs: Any) -> tuple[list[ModelT], int]: # type: ignore
        """List records with total count.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            a tuple containing The list of instances, after filtering applied, and a count of records returned by query, ignoring pagination.
        """
        result_query = self._apply_filters(
            filters,
            apply_pagination=False,
            queryset=self.model_type.query
        ).filter(**kwargs)
        result_query._order_by = None

        count = await result_query.count()
        result = await result_query.all()
        return result, count


    async def list(self, *filters: Any, **kwargs: Any) -> list[ModelT]:
        """Get a list of instances, optionally filtered.

        Args:
            *filters: filters for specific filtering operations
            **kwargs: Instance attribute value filters.

        Returns:
            The list of instances, after filtering applied
        """
        queryset = self._apply_filters(filters, apply_pagination=True, queryset=self.model_type.query)
        return await queryset.filter(**kwargs).all()


    @staticmethod
    def check_not_found(item_or_none: ModelT | None) -> T:
        """Raise :class:`NotFoundError` if ``item_or_none`` is ``None``.

        Args:
            item_or_none: Item (:class:`T <T>`) to be tested for existence.

        Returns:
            The item, if it exists.
        """
        if item_or_none is None:
            raise ObjectNotFound("No item found when one was expected")
        return item_or_none


    @classmethod
    async def check_health(cls) -> bool:
        """Perform a health check on the database.

        Args:
            session: through which we run a check statement

        Returns:
            ``True`` if healthy.
        """
        
        await cls.model_type.query.database.execute(text("SELECT 1"))
        return await cls.model_type.query.database.fetch_val() == 1

    
    @classmethod
    def get_id_attribute_value(cls, item: ModelT | type[ModelT], id_attribute: str | None = None) -> Any:
        """Get value of attribute named as :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` on ``item``.

        Args:
            item: Anything that should have an attribute named as :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` value.
            id_attribute: Allows customization of the unique identifier to use for model fetching.
                Defaults to `None`, but can reference any surrogate or candidate key for the table.

        Returns:
            The value of attribute on ``item`` named as :attr:`id_attribute <AbstractAsyncRepository.id_attribute>`.
        """
        return getattr(item, id_attribute if id_attribute is not None else cls.id_attribute)


    @classmethod
    def set_id_attribute_value(cls, item_id: Any, item: T, id_attribute: str | None = None) -> T:
        """Return the ``item`` after the ID is set to the appropriate attribute.

        Args:
            item_id: Value of ID to be set on instance
            item: Anything that should have an attribute named as :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` value.
            id_attribute: Allows customization of the unique identifier to use for model fetching.
                Defaults to `None`, but can reference any surrogate or candidate key for the table.

        Returns:
            Item with ``item_id`` set to :attr:`id_attribute <AbstractAsyncRepository.id_attribute>`
        """
        setattr(item, id_attribute if id_attribute is not None else cls.id_attribute, item_id)
        return item
    
    def filter_collection_by_kwargs(self, collection: Collection[ModelT], /, **kwargs: Any) -> Collection[ModelT]:
        return super().filter_collection_by_kwargs(collection, **kwargs)

class AsyncSlugRepository(AsyncRepository[ModelT]):
    """Extends the repository to include slug model features.."""

    async def get_by_slug(
        self,
        slug: str,
        **kwargs: Any,
    ) -> ModelT | None:
        """Select record by slug value."""
        return await self.get_one_or_none(slug=slug)

    async def get_available_slug(
        self,
        value_to_slugify: str,
        **kwargs: Any,
    ) -> str:
        """Get a unique slug for the supplied value.

        If the value is found to exist, a random 4 digit character is appended to the end.

        Override this method to change the default behavior

        Args:
            value_to_slugify (str): A string that should be converted to a unique slug.
            **kwargs: stuff

        Returns:
            str: a unique slug for the supplied value.  This is safe for URLs and other unique identifiers.
        """
        slug = slugify(value_to_slugify)
        if await self._is_slug_unique(slug):
            return slug
        random_string = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))  # noqa: S311
        return f"{slug}-{random_string}"

    async def _is_slug_unique(
        self,
        slug: str,
        **kwargs: Any,
    ) -> bool:
        self.model_type.meta
        return await self.exists(slug=slug) is False
