from fimbu.db import fields
from fimbu.contrib.auth.adapters.mixins import BaseUserMixin
from fimbu.db.utils import get_db_connection

_, registry = get_db_connection()


class User(BaseUserMixin):

    user_name = fields.CharField(max_length=255)
    first_name = fields.CharField(max_length=255)
    last_name = fields.CharField(max_length=255)
    last_login = fields.DateTimeField(auto_now=True)

    class Meta:
        registry = registry
