from typing import Any, Coroutine
from uuid import UUID
from datetime import datetime

from edgy.core.db.models.model import Model
from fimbu.db import fields
from fimbu.contrib.auth.adapters.mixins import BaseUserMixin, BaseRoleMixin, BaseUUIDMixin
from fimbu.db.utils import get_db_connection
from fimbu.utils.text import slugify

_, registry = get_db_connection()


class User(BaseUserMixin):
    first_name: str = fields.CharField(max_length=255)
    last_name: str = fields.CharField(max_length=255)
    last_login: datetime = fields.DateTimeField(auto_now=True)

    class Meta:
        registry = registry


class Role(BaseRoleMixin):
    slug: str = fields.CharField(max_length=80)
    name: str = fields.CharField(max_length=80)
    description: str = fields.CharField(max_length=255)


    async def save(self, *args, **kwargs: Any) -> Coroutine[Any, Any, type[Model] | Any]:
        self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        registry = registry


class UserRole(BaseUUIDMixin):
    user: UUID = fields.ForeignKey(
        to=User,
        related_name="user_roles",
    )
    role: UUID = fields.ForeignKey(
        to=Role,
        related_name="role_users",
    )
    assigned_at: datetime = fields.DateTimeField(auto_now=True)

    class Meta:
        registry = registry
