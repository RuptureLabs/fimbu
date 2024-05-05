from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

import anyio
from fimbu.core.utils import get_pydantic_fields
from fimbu.db.exceptions import DuplicateRecordError, ObjectNotFound
from click import echo, group, option, prompt
from fimbu.cli._utils import FimbuGroup

from fimbu.contrib.auth.utils import get_auth_plugin, get_user_service

if TYPE_CHECKING:
    from litestar import Litestar


@group(cls=FimbuGroup, name="users")
def user_management_group() -> None:
    """Manage users."""


@user_management_group.command(
    name="create-user",
    help="Create a new user in the database.",
    context_settings={"ignore_unknown_options": True, "allow_extra_args": True},
)
def create_user(
    app: Litestar,
) -> None:
    """Create a new user in the database."""
    kwargs: dict[str, str | int | float | bool] = {}
    
    auth_config = get_auth_plugin(app)._config

    req, _ = get_pydantic_fields(auth_config.user_model)

    for name in req:
        is_pwd = name == "password_hash"
        kwargs[name] = prompt(
            f"User {name}" if not is_pwd else "User password",
            hide_input=is_pwd,
            confirmation_prompt=is_pwd,
        )



    async def _create_user() -> None:
        user_service = get_user_service(app)
        if 'password_hash' in kwargs:
            kwargs['password_hash'] = user_service.password_manager.hash(kwargs['password_hash'])
        
        try:
            user = await user_service.add_user(
                user=auth_config.user_model(**kwargs),
                activate=True,
                verify=False,
            )
            echo(f"User {user.id} created successfully.")
        except DuplicateRecordError as e:
            # could be caught IntegrityError or unique collision
            msg = e.__cause__ if e.__cause__ else e
            echo(f"Error: {msg}", err=True)
            sys.exit(1)
        except TypeError as e:
            echo(f"Error: {e}", err=True)
            sys.exit(1)

    anyio.run(_create_user)


@user_management_group.command(name="create-role", help="Create a new role in the database.")
@option("--name")
@option("--description")
def create_role(app: Litestar, name: str | None, description: str | None) -> None:
    """Create a new role in the database."""

    auth_config = get_auth_plugin(app)._config

    name = name or prompt("Role name")

    async def _create_role() -> None:
        user_service = get_user_service(app)
        if auth_config.role_model is None:
            echo("Role model is not defined")
            sys.exit(1)
        try:
            role = await user_service.add_role(auth_config.role_model(name=name, description=description))
            echo(f"Role {role.id} created successfully.")
        except DuplicateRecordError as e:
            # could be caught IntegrityError or unique collision
            msg = e.__cause__ if e.__cause__ else e
            echo(f"Error: {msg}", err=True)
            sys.exit(1)

    anyio.run(_create_role)


@user_management_group.command(name="assign-role", help="Assign a role to a user.")
@option("--email")
@option("--role")
def assign_role(
    app: Litestar,
    email: str | None,
    role: str | None,
) -> None:
    """Assign a role to a user."""

    auth_config = get_auth_plugin(app)._config
    if auth_config.role_model is None:
        echo("Role model is not defined")
        sys.exit(1)

    email = email or prompt("User email")
    role = role or cast(str, prompt("Role", type=str))

    async def _assign_role() -> None:
        user_service = get_user_service(app)
        try:
            user = await user_service.get_user_by(email=email)
            if user is None:
                raise ObjectNotFound()
        except ObjectNotFound:
            echo("User not found", err=True)
            sys.exit(1)
        try:
            role_db = await user_service.get_role_by_name(role)  # type: ignore[arg-type]
        except ObjectNotFound:
            echo("Role not found", err=True)
            sys.exit(1)
        await user_service.assign_role(user.id, role_db.id)
        echo(f"Role {role} assigned to user {email} successfully.")

    anyio.run(_assign_role)
