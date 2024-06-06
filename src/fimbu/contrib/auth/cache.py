from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic_core import from_json

from fimbu.contrib.auth.models import User, PermissionScope, Permission
from fimbu.contrib.auth.utils import get_user_model

if TYPE_CHECKING:
    from uuid import UUID
    from typing import Any
    from fimbu.contrib.auth.protocols import UserT
    from fimbu.contrib.auth.config import AuthConfig
    from pydantic import BaseModel



UserModel: BaseModel = get_user_model()


def encode_user(user: UserT | BaseModel) -> str:
    """Encode a user into a dictionary."""
    user.password_hash = '******'
    return user.model_dump_json()



def decode_user(user: str) -> UserT:
    """Decode a user from a JSON string."""
    return UserModel.model_validate(from_json(user))



async def retrieve_user_from_cache(self, user_id: UUID, config: AuthConfig) -> UserT:
    """Get a user from the cache.

    Args:
        user_id: The user ID.
    """

    user_key = f"user:{user_id}"
    exists = await config.auth_store.exists(user_key)

    if not exists:
        repository = config.user_repository_class(
            model_type=config.user_model
        )
        user = await repository.get(user_id)
        await config.auth_store.set(user_key, encode_user(user))
        return user
    
    else:
        user_json = await config.auth_store.get(user_key)
        return decode_user(user_json)
