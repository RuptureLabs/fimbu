from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from fimbu.db.exceptions import ObjectNotFound
from fimbu.contrib.auth.utils import get_auth_plugin

__all__ = ["jwt_retrieve_user_handler", "session_retrieve_user_handler"]


if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.contrib.jwt import Token

    from fimbu.contrib.auth.adapters.protocols import UserT


async def session_retrieve_user_handler(session: dict[str, Any], connection: ASGIConnection) -> UserT | None:
    """Get a user from the database based on session info.

    Args:
        session: Litestar session.
        connection: The ASGI connection.
    """

    litestar_users_config = get_auth_plugin(connection.app)._config
    repository = litestar_users_config.user_repository_class(
        model_type=litestar_users_config.user_model
    )
    try:
        user_id = session.get("user_id")
        if user_id is None:
            return None
        user = await repository.get(UUID(user_id))
        
        if user.is_active and not user.is_verified:
            return user  # type: ignore[no-any-return]
    except ObjectNotFound:
        pass
    return None


async def jwt_retrieve_user_handler(token: Token, connection: ASGIConnection) -> UserT | None:
    """Get a user from the database based on JWT info.

    Args:
        token: Encoded JWT.
        connection: The ASGI connection.
    """

    litestar_users_config = get_auth_plugin(connection.app)._config
    repository = litestar_users_config.user_repository_class(
        model_type=litestar_users_config.user_model
    )
    try:
        user = await repository.get(UUID(token.sub))
        if user.is_active and user.is_verified:
            return user  # type: ignore[no-any-return]
    except ObjectNotFound:
        pass
    return None
