import os
from pathlib import Path
import click
from click import Context
from rich_click import Path as ClickPath
import typing

from litestar.cli.commands import core, sessions, schema
from edgy.cli.operations import (
    check,
    current,
    downgrade,
    edit,
    heads,
    history,
    init,
    # inspect_db, # Use custom command
    list_templates,
    makemigrations,
    merge,
    migrate,
    revision,
    # shell, # Doesn't work well with Litestar.lifespan
    show,
    stamp,
)

from fimbu.db.utils import get_db_registry

from .commands import start_app, start_project, shell, inspect_db


from fimbu.core.utils import setup_fimbu

setup_fimbu() # setup fimbu cli

from fimbu.cli._utils import FimbuExtensionGroup, FimbuGroup
from fimbu.cli.env import FimbuEnv
from fimbu.conf import settings


from fimbu.conf import settings


P = typing.ParamSpec("P")
T = typing.TypeVar("T")


__all__ = [
    "fimbu_cli",
    "FimbuGroup",
]


@click.group(cls=FimbuExtensionGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--app",
    "app_path",
    help="Module path to a Litestar application",
    default=settings.ASGI_APPLICATION,
    )
@click.option(
    "--app-dir",
    help="Look for APP in the specified directory, by adding this to the PYTHONPATH. Defaults to the current working directory.",
    default=None,
    type=ClickPath(dir_okay=True, file_okay=False, path_type=Path),
    show_default=False,
)
@click.pass_context
def fimbu_cli(ctx: Context, app_path: str | None, app_dir: Path | None = None):
    db = get_db_registry().get_primary_db()
    
    if db is not None:
        os.environ.setdefault("EDGY_DATABASE_URL", db.url._url)

    if ctx.obj is None:
        ctx.obj = lambda: FimbuEnv.from_env(app_path=app_path, app_dir=app_dir)


@fimbu_cli.command(name="version")
def version_command() -> None:
    """Show the currently installed Litestar version."""
    from litestar import __version__ as liver
    from fimbu import __version__ as fiver
    from edgy import __version__ as edver

    click.echo("""Fimbu version: {}
litestar: {}
edgy: {}
""".format(fiver, liver.formatted(short=False), edver))


fimbu_cli.add_command(core.info_command)
fimbu_cli.add_command(core.routes_command)
fimbu_cli.add_command(version_command)
fimbu_cli.add_command(core.run_command)
fimbu_cli.add_command(sessions.sessions_group)
fimbu_cli.add_command(schema.schema_group)

fimbu_cli.add_command(start_app, name="startapp")
fimbu_cli.add_command(start_project, name="startproject")

fimbu_cli.add_command(list_templates)
fimbu_cli.add_command(init, name="init")
fimbu_cli.add_command(revision, name="revision")
fimbu_cli.add_command(makemigrations, name="makemigrations")
fimbu_cli.add_command(edit, name="edit")
fimbu_cli.add_command(merge, name="merge")
fimbu_cli.add_command(migrate, name="migrate")
fimbu_cli.add_command(downgrade, name="downgrade")
fimbu_cli.add_command(show, name="show")
fimbu_cli.add_command(history, name="history")
fimbu_cli.add_command(heads, name="heads")
fimbu_cli.add_command(current, name="current")
fimbu_cli.add_command(stamp, name="stamp")
fimbu_cli.add_command(check, name="check")
fimbu_cli.add_command(shell, name="shell")
fimbu_cli.add_command(inspect_db, name="inspectdb")
