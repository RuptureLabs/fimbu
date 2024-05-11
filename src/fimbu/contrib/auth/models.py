from typing import Coroutine, Any
from uuid import UUID
from datetime import datetime
from fimbu.db import Model, fields, CASCADE
from fimbu.db.utils import get_db_connection
from fimbu.db.mixins import UUIDMixin, UserMixin
from fimbu.contrib.auth.utils import installed_native_auth, has_custom_model, get_user_model
from fimbu.utils.text import slugify


registry, _ = get_db_connection()


class User(Model, UserMixin):
    """User model"""
    username: str = fields.CharField(max_length=75)


    class Meta:
        registry = registry
        abstract = has_custom_model()


class Role(Model, UUIDMixin):
    """User model"""
    name: str = fields.CharField(max_length=75)
    slug: str = fields.CharField(max_length=75)
    description: str = fields.TextField()


    async def save(self, *args, **kwargs: Any) -> Coroutine[Any, Any, type[Model] | Any]:
        self.slug = slugify(self.name)
        return await super().save(*args, **kwargs)


    class Meta:
        registry = registry
        abstract = not installed_native_auth()



UserModel = get_user_model()

class UserRole(Model, UUIDMixin):
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
        abstract = not installed_native_auth()


class UserOauthAccount(Model, UUIDMixin):
    """User Oauth Account"""

    user: UUID = fields.ForeignKey(UserModel, on_delete=CASCADE)
    oauth_name: str = fields.CharField(max_length=100, index=True)
    access_token: str = fields.CharField(max_length=1024, nullable=False)
    expires_at: int | None = fields.IntegerField(nullable=True)
    refresh_token: str = fields.CharField(max_length=1024, nullable=True)
    account_id: str = fields.CharField(max_length=320, index=True)
    account_email: str =  fields.CharField(max_length=320)


    class Meta:
        registry = registry
        abstract = not installed_native_auth()
