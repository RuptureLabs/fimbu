from uuid import UUID
from datetime import datetime
from fimbu.db import fields
from fimbu.contrib.auth.adapters.mixins import BaseUserMixin, BaseRoleMixin
from fimbu.db.utils import get_db_connection

_, registry = get_db_connection()


class User(BaseUserMixin):
    id: UUID = fields.IntegerField(primary_key=True)
    user_name: str = fields.CharField(max_length=255)
    first_name: str = fields.CharField(max_length=255)
    last_name: str = fields.CharField(max_length=255)
    last_login: datetime = fields.DateTimeField(auto_now=True)

    class Meta:
        registry = registry


class Role(BaseRoleMixin):
    id: UUID = fields.IntegerField(primary_key=True)
    name: str = fields.CharField(max_length=80)
    description: str = fields.CharField(max_length=255)

    class Meta:
        registry = registry
