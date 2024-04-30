"""
Fimbu db exceptions
"""

from edgy.exceptions import (
    ObjectNotFound,
    MultipleObjectsReturned,
    FieldDefinitionError,
    SignalError,
    ImproperlyConfigured,
    ForeignKeyBadConfigured,
    RelationshipIncompatible,
    ModelReferenceError,
    DuplicateRecordError,
    QuerySetError,
    ModelReferenceError,
    SchemaError,
    RelationshipNotFound,
    CommandEnvironmentError
)

from fimbu.core.exceptions import FimbuException

__all__ = [
    "ObjectNotFound",
    "MultipleObjectsReturned",
    "FieldDefinitionError",
    "SignalError",
    "ImproperlyConfigured",
    "ForeignKeyBadConfigured",
    "RelationshipIncompatible",
    "ModelReferenceError",
    "DuplicateRecordError",
    "QuerySetError",
    "ModelReferenceError",
    "SchemaError",
    "RelationshipNotFound",
    "CommandEnvironmentError"
]


class DatabaseNotFound(FimbuException):
    pass


class RepositoryError(FimbuException):
    """Base repository exception type."""
