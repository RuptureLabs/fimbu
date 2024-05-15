from __future__ import annotations

from fimbu.contrib.auth.utils import get_auth_plugin

__all__ = ["provide_user_service"]


from litestar import Request
from litestar.datastructures import State

from fimbu.contrib.auth.service import UserService


async def provide_user_service(state: State, request: Request) -> UserService:
    """Instantiate service and repository for use with DI.

    Args:
        request: The incoming request
        state: The application.state instance
    """
    auth_config = get_auth_plugin(request.app)._config
    user_repository = auth_config.user_repository_class(auth_config.user_model)

    return auth_config.user_service_class(
        user_repository=user_repository,
        secret=auth_config.secret,
        hash_schemes=auth_config.hash_schemes,
    )
