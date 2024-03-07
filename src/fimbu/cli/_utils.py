from __future__ import annotations

import importlib
import inspect
import os
import sys
from dataclasses import dataclass
from functools import wraps
from importlib.util import find_spec
from itertools import chain
from os import getenv
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable, Generator, Iterable, Sequence, TypeVar, cast

from click import ClickException, Command, Context, Group, pass_context
from rich import get_console
from rich.table import Table
from typing_extensions import ParamSpec, get_type_hints

from litestar import Litestar, __version__
from litestar.middleware import DefineMiddleware
from litestar.utils import get_name
from litestar.cli._utils import (
    LitestarCLIException,
)

from .env import FimbuEnv

if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points



if TYPE_CHECKING:
    from litestar.types import AnyCallable





__all__ = (
    "FimbuExtensionGroup",
    "FimbuGroup",
)


P = ParamSpec("P")
T = TypeVar("T")


AUTODISCOVERY_FILE_NAMES = ["app", "application"]

console = get_console()



class FimbuGroup(Group):
    """:class:`click.Group` subclass that automatically injects ``app`` and ``env` kwargs into commands that request it.

    Use this as the ``cls`` for :class:`click.Group` if you're extending the internal CLI with a group. For ``command``s
    added directly to the root group this is not needed.
    """

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, Command] | Sequence[Command] | None = None,
        **attrs: Any,
    ) -> None:
        """Init ``LitestarGroup``"""
        self.group_class = FimbuGroup
        super().__init__(name=name, commands=commands, **attrs)

    def add_command(self, cmd: Command, name: str | None = None) -> None:
        """Add command.

        If necessary, inject ``app`` and ``env`` kwargs
        """
        if cmd.callback:
            cmd.callback = _inject_args(cmd.callback)
        super().add_command(cmd)

    def command(self, *args: Any, **kwargs: Any) -> Callable[[AnyCallable], Command] | Command:  # type: ignore[override]
        # For some reason, even when copying the overloads + signature from click 1:1, mypy goes haywire
        """Add a function as a command.

        If necessary, inject ``app`` and ``env`` kwargs
        """

        def decorator(f: AnyCallable) -> Command:
            f = _inject_args(f)
            return cast("Command", Group.command(self, *args, **kwargs)(f))

        return decorator


class FimbuExtensionGroup(FimbuGroup):
    """``LitestarGroup`` subclass that will load Litestar-CLI extensions from the `litestar.commands` entry_point.

    This group class should not be used on any group besides the root ``litestar_group``.
    """

    def __init__(
        self,
        name: str | None = None,
        commands: dict[str, Command] | Sequence[Command] | None = None,
        **attrs: Any,
    ) -> None:
        """Init ``LitestarExtensionGroup``"""
        super().__init__(name=name, commands=commands, **attrs)
        self._prepare_done = False

        for entry_point in entry_points(group="litestar.commands"):
            command = entry_point.load()
            _wrap_commands([command])
            self.add_command(command, entry_point.name)

    def _prepare(self, ctx: Context) -> None:
        if self._prepare_done:
            return

        if isinstance(ctx.obj, FimbuEnv):
            env: FimbuEnv | None = ctx.obj
        else:
            try:
                env = ctx.obj = FimbuEnv.from_env(ctx.params.get("app_path"), ctx.params.get("app_dir"))
            except LitestarCLIException:
                env = None

        if env:
            for plugin in env.app.plugins.cli:
                plugin.on_cli_init(self)

        self._prepare_done = True

    def make_context(
        self,
        info_name: str | None,
        args: list[str],
        parent: Context | None = None,
        **extra: Any,
    ) -> Context:
        ctx = super().make_context(info_name, args, parent, **extra)
        self._prepare(ctx)
        return ctx

    def list_commands(self, ctx: Context) -> list[str]:
        self._prepare(ctx)
        return super().list_commands(ctx)


def _inject_args(func: Callable[P, T]) -> Callable[P, T]:
    """Inject the app instance into a ``Command``"""
    params = inspect.signature(func).parameters

    @wraps(func)
    def wrapped(ctx: Context, /, *args: P.args, **kwargs: P.kwargs) -> T:
        needs_app = "app" in params
        needs_env = "env" in params
        if needs_env or needs_app:
            # only resolve this if actually requested. Commands that don't need an env or app should be able to run
            # without
            if not isinstance(ctx.obj, FimbuEnv):
                ctx.obj = ctx.obj()
            env = ctx.ensure_object(FimbuEnv)
            if needs_app:
                kwargs["app"] = env.app
            if needs_env:
                kwargs["env"] = env

        if "ctx" in params:
            kwargs["ctx"] = ctx

        return func(*args, **kwargs)

    return pass_context(wrapped)


def _wrap_commands(commands: Iterable[Command]) -> None:
    for command in commands:
        if isinstance(command, Group):
            _wrap_commands(command.commands.values())
        elif command.callback:
            command.callback = _inject_args(command.callback)
