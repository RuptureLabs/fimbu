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
