from datetime import datetime
from typing import Coroutine, Any, Union
from uuid import UUID
from fimbu.db import Model, fields, CASCADE, ObjectNotFound
from fimbu.db.utils import get_db_connection
from fimbu.db.mixins import UUIDMixin, UserMixin
from fimbu.contrib.auth.utils import installed_native_auth, has_custom_model, get_user_model
from fimbu.utils.text import slugify
from fimbu.contrib.auth.protocols import UserT


_, registry = get_db_connection()


class User(UserMixin):
    """User model"""
    username: str = fields.CharField(max_length=75)

    class Meta:
        registry = registry
        abstract = has_custom_model()


UserModel = get_user_model()


class PermissionScope(UUIDMixin):
    """User Permission Scope model"""
    name: str = fields.CharField(max_length=75)
    slug: str = fields.CharField(max_length=75, index=True, unique=True, default='')
    codename: str = fields.CharField(max_length=12, index=True, unique=True)
    default: bool = fields.BooleanField(default=False)
    default_permissins = fields.CharField(max_length=6, default='R')
    description: str = fields.TextField(null=True, default=None)


    async def save(self, *args, **kwargs: Any) -> Coroutine[Any, Any, type[Model] | Any]:
        self.slug = slugify(self.name)
        self.default_permissins = str(self.default_permissins).upper()
        return await super().save(*args, **kwargs)
    

    async def suscribe_user(self, user: UserT) -> "Permission":
        """
        Subscribe a user to this permission scope
        
        args:
            user (User): The user to subscribe.

        Returns:
            Permission: The created & saved permission.
        """
        return await self.create_permission(user).save()


    async def unscribe_user(self, user: UserT) -> Union["Permission", None]:
        """
        Revoke a user from this permission scope, removing all user's permissions.

        Args:
            user (User): The user to revoke.
        """
        try:
            permission = await Permission.query.get(user=user, scope=self)
            await permission.delete()
        except ObjectNotFound:
            permission = None

        return permission


    def create_permission(self, user: UserT) -> "Permission":
        """
        Create a new permission for this permission scope

        Args:
            user (User): The user to create the permission for.

        Returns:
            Permission: The created permission.
        
        """
        return Permission(
            user=user, 
            scope=self, 
            **self.parse_default_permissions(self.default_permissins)
        )
    

    @staticmethod
    def parse_default_permissions(permissions: str) -> dict[str, bool]:
        """
        Parse default permissions into a dictionary of permissions.

        Args:
            permissions (str): A string containing permission characters 
                            (e.g., "RWU" for read, write, and update).

        Returns:
            dict[str, bool]: A dictionary mapping permission names to True
                            for the specified permissions.
        """
        perms_map = {
            'R': 'can_read',
            'W': 'can_write',
            'U': 'can_update',
            'D': 'can_delete',
            'A': 'can_approve'
        }

        return {perms_map[p]: True for p in permissions if p in perms_map}


    class Meta:
        registry = registry
        abstract = not installed_native_auth()



class Permission(UUIDMixin):
    """User Permission model"""
    user: UUID = fields.ForeignKey(
        UserModel,
        related_name="permissions",
        on_delete=CASCADE
    )
    scope: UUID = fields.ForeignKey(
        PermissionScope,
        related_name="permissions",
        on_delete=CASCADE
    )
    assigned_at: datetime = fields.DateTimeField(auto_now_add=True)
    can_read: bool = fields.BooleanField(default=False)
    can_write: bool = fields.BooleanField(default=False)
    can_update: bool = fields.BooleanField(default=False)
    can_delete: bool = fields.BooleanField(default=False)
    can_approve: bool = fields.BooleanField(default=False)


    class Meta:
        registry = registry
        abstract = not installed_native_auth()
