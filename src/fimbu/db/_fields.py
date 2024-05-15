from typing import Any
from datetime import datetime
from edgy.core.db.fields.core import FieldFactory, UUIDField
from sqlalchemy.dialects.postgresql import UUID

from fimbu.db.types import (
    GUID, JsonB, DateTimeUTC, BigIntIdentity,
    EncryptedString, EncryptedText,
)


class GUIDField(UUIDField):
    _type = UUID

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        return GUID(**kwargs)


class JsonBField(FieldFactory, str):
    _type = JsonB

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        return JsonB(**kwargs)
    

class DateTimeUTCField(FieldFactory, datetime):
    _type = datetime

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        return DateTimeUTC(**kwargs)    


class BigIntIdentityField(FieldFactory, int):
    _type = int

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        return BigIntIdentity(**kwargs)


class EncryptedStringField(FieldFactory, str):
    _type = str

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        return EncryptedString(**kwargs)
    

class EncryptedTextField(FieldFactory, str):
    _type = str

    @classmethod
    def get_column_type(cls, **kwargs: Any) -> Any:
        return EncryptedText(**kwargs)
