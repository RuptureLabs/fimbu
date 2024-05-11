from __future__ import annotations

from typing import TYPE_CHECKING

from litestar.exceptions import NotAuthorizedException, PermissionDeniedException

__all__ = ["roles_accepted", "roles_required"]


if TYPE_CHECKING:
    from litestar.connection import ASGIConnection
    from litestar.handlers import BaseRouteHandler
    from litestar.types import Guard


def roles_accepted(*roles: str) -> Guard:
    """Get a [Guard][litestar.types.Guard] callable and inject authorized role names.

    Args:
        roles: Iterable of authorized role names.

    Returns:
        Litestar [Guard][litestar.types.callable_types.Guard] callable
    """

    def roles_accepted_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
        """Authorize a request if any of the user's roles matches any of the supplied roles."""
        if any(role.name in roles for role in connection.user.roles):
            return
        raise NotAuthorizedException()

    return roles_accepted_guard


def roles_required(*roles: str) -> Guard:
    """Get a [Guard][litestar.types.Guard] callable and inject authorized role names.

    Args:
        roles: Iterable of authorized role names.
    """

    def roles_required_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
        """Authorize a request if the user's roles matches all of the supplied roles."""
        user_role_names = [role.name for role in connection.user.roles]
        if all(role in user_role_names for role in roles):
            return
        raise NotAuthorizedException()

    return roles_required_guard


def requires_active_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Request requires active user.

    Verifies the request user is active.

    Args:
        connection (ASGIConnection): HTTP Request
        _ (BaseRouteHandler): Route handler

    Raises:
        PermissionDeniedException: Permission denied exception
    """
    if connection.user.is_active:
        return
    msg = "Inactive account"
    raise PermissionDeniedException(msg)


def requires_superuser(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Request requires active superuser.

    Args:
        connection (ASGIConnection): HTTP Request
        _ (BaseRouteHandler): Route handler

    Raises:
        PermissionDeniedException: Permission denied exception

    Returns:
        None: Returns None when successful
    """
    if connection.user.is_superuser:
        return
    raise PermissionDeniedException(detail="Insufficient privileges")


def requires_verified_user(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    """Verify the connection user is a superuser.

    Args:
        connection (ASGIConnection): Request/Connection object.
        _ (BaseRouteHandler): Route handler.

    Raises:
        PermissionDeniedException: Not authorized

    Returns:
        None: Returns None when successful
    """
    if connection.user.is_verified:
        return
    raise PermissionDeniedException(detail="User account is not verified.")
