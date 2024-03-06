import click
from litestar.cli._utils import LitestarExtensionGroup
from litestar.cli.commands import core, sessions, schema

@click.group(cls=LitestarExtensionGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
def fimbu_cli():
    pass

fimbu_cli.add_command(core.info_command)
fimbu_cli.add_command(core.routes_command)
fimbu_cli.add_command(core.version_command)
fimbu_cli.add_command(core.run_command)
fimbu_cli.add_command(sessions.sessions_group)
fimbu_cli.add_command(schema.schema_group)
