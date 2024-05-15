from typing import Any, Generic, Collection
from edgy import ObjectNotFound
from litestar.repository.abc import AbstractAsyncRepository
from litestar.repository.filters import FilterTypes
from fimbu.core.types import ModelT, T



__all__ = ["Repository"]

class Repository(AbstractAsyncRepository[ModelT], Generic[ModelT]):
    """The base repository class."""

    model_type: type[ModelT]

    def __init__(self, model_type: type[ModelT], **kwargs: Any) -> None:
        """Repository constructors accept arbitrary kwargs."""
        self.model_type = model_type
        super().__init__(**kwargs)


    async def add(self, data: ModelT) -> ModelT:
        """Add ``data`` to the collection."""
        return await data.save()
    

    async def add_many(self, data: list[ModelT]) -> list[ModelT]:
        """Add multiple ``data`` to the collection."""
        return await self.model_type.query.bulk_create(data)
    

    async def count(self, *filters: Any, **kwargs: Any) -> int:
        """Get the count of records returned by a query.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            The count of instances
        """
        return await self.model_type.query.filter(**kwargs).count()
    
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
        
        return self.model_type.query.exists(**kwargs)


    async def get(self, item_id: Any, **kwargs: Any) -> ModelT:
        """Get instance identified by ``item_id``.

        Args:
            item_id: Identifier of the instance to be retrieved.
            **kwargs: Additional arguments

        Returns:
            The retrieved instance.

        Raises:
            ObjectNotFound: If no instance found identified by ``item_id``.
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
        try:
            return await self.get_one(**kwargs)
        except ObjectNotFound:
            return None


    async def update(self, data: ModelT, **kwargs: Any) -> ModelT:
        """Update instance with the attribute values present on ``data``.

        Args:
            data: An instance that should have a value for :attr:`id_attribute <AbstractAsyncRepository.id_attribute>` that exists in the
                collection.

        Returns:
            The updated instance.
        """
        return await data.update(**kwargs)


    async def update_many(self, data: list[ModelT]) -> list[ModelT]:
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
    

    async def upsert(self, **kwargs: Any) -> ModelT:
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


    async def list_and_count(self, *filters: FilterTypes, **kwargs: Any) -> tuple[list[ModelT], int]:
        """List records with total count.

        Args:
            *filters: Types for specific filtering operations.
            **kwargs: Instance attribute value filters.

        Returns:
            a tuple containing The list of instances, after filtering applied, and a count of records returned by query, ignoring pagination.
        """

    
    async def list(self, *filters: Any, **kwargs: Any) -> list[ModelT]:
        """Get a list of instances, optionally filtered.

        Args:
            *filters: filters for specific filtering operations
            **kwargs: Instance attribute value filters.

        Returns:
            The list of instances, after filtering applied
        """
        return await self.model_type.query.filter(*filters, **kwargs).all()


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
