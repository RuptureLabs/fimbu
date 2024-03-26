from __future__ import annotations
from typing import List, Any, Callable, Optional, Sequence
import os, sys
import select
import stat
import shutil
from importlib.util import find_spec
import nest_asyncio

import black
import click
from jinja2 import Environment, FileSystemLoader

from edgy import Registry
from edgy.cli.env import MigrationEnv
from edgy.cli.operations.shell.base import handle_lifespan_events
from edgy.core.sync import execsync
from edgy.utils.inspect import InspectDB

import fimbu
from fimbu.core.exceptions import CommandError
from fimbu.utils.crypto import get_random_secret_key 


STATIC_DIR = 'static'
TEMPLATES_DIR = 'templates'

__all__ = [
    'start_project',
    'start_application',
]

@click.command()
@click.argument(
    'name',
    required=True,
    type=str
)
@click.option(
    '-d', '--dest', 'dest', 
    default='.', 
    type=str,
    show_default=True,
    help="The path destination of the project"
)

@click.option(
    '-s', '--secret-key-size', 'secret_key_size',
    default=32,
    type=click.Choice([16, 24, 32]),
    help="The size of the secret key"
)
def start_project(name: str, dest: str, secret_key_size: int):
    """A template starter for fimbu project"""
    starter = Starter(name=name, application=False, directory=dest, secret_key_size=int(secret_key_size))
    starter.execute()


@click.command()
@click.argument(
    'name',
    nargs=1,
    type=str
)
@click.option(
    '-d', '--dest', 'dest',
    default='.',
    type=str,
    show_default=True,
    help="The path destination of the application"
)
def start_app(name: str, dest: str):
    """A template starter for fimbu application"""
    starter = Starter(name=name, application=True, directory=dest, secret_key_size=16)
    starter.execute()


class Starter(object):
    
    def __init__(self, **options):
        self.secret_key_size = options['secret_key_size']
        self.name = options['name']
        self.options = options


    def execute(self):
        self.app_or_project_name = self.name

        self.is_application = self.options['application'] == True
        self.a_or_an = "an" if self.is_application else "a"

        target = self.options['directory']
        self.validate_name(self.name)

        base_name = self.name
        camel_case_name = self.camel_case(self.name)
        snake_case_name = self.snake_case(self.name)

        if target is None:
            root_dir = os.path.join(os.getcwd(), snake_case_name)
            try:
                os.makedirs(root_dir)
            except FileExistsError as e:
                raise CommandError("'%s' already exists" % root_dir) from e
            except OSError as e:
                raise CommandError from  e
        else:
            target = target[0]
            root_dir = os.path.abspath(os.path.expanduser(target))
            if self.is_application:
                self.validate_name(os.path.basename(root_dir), 'directory')
                
            if not os.path.exists(root_dir):
                raise CommandError(
                    "Destination directory '%s' does not "
                    "exist, please create it first." % root_dir
                )


        template_context = {
            "oya_version": fimbu.__version__,
            'secret_key' : get_random_secret_key(self.secret_key_size),
            'base_name' : base_name,
            'camel_case_name' : camel_case_name,
            'snake_case_name' : snake_case_name,
        }


        if self.is_application:
            _tpl_dir = "application"
        else:
            _tpl_dir = "project"


        TEMPLATE_BASE_DIR = os.path.join(os.path.dirname(__file__), 'templates')
        TEMPLATE_DIR = os.path.join(TEMPLATE_BASE_DIR, _tpl_dir)

        tree = os.walk(TEMPLATE_DIR)

        if self.is_application and target is not None:
            output_dir_path = os.path.join(root_dir, snake_case_name)
        elif self.is_application:
            output_dir_path = root_dir
        else:
            output_dir_path = os.path.join(root_dir, camel_case_name)

        if not os.path.exists(output_dir_path):
            os.mkdir(output_dir_path)

        if not self.is_application:
            self.copy_jinja_file(TEMPLATE_BASE_DIR, 'fimbu.ini.jinja', root_dir, template_context)
            self.mkdir(os.path.join(root_dir, STATIC_DIR))
            self.mkdir(os.path.join(root_dir, TEMPLATES_DIR))

        for directory in tree:
            dir_path, sub_dir_names, files_names = directory


            for sub_dir_name in sub_dir_names:
                if sub_dir_name.startswith("_"):
                    continue

                sub_dir_path = os.path.join(dir_path, sub_dir_name)
                if not os.path.exists(sub_dir_path):
                    os.mkdir(sub_dir_path)

                self.make_writeable(sub_dir_path)


            for file_name in files_names:
                if file_name.startswith("_") and file_name != "__init__.py.jinja":
                    continue

                extension = file_name.rsplit('.')[0]
                if extension in (".pyo", ".pyc", ".py.class"):
                    continue

                if file_name.endswith('.jinja'):
                    self.copy_jinja_file(dir_path, file_name, output_dir_path, template_context)
                else:
                    shutil.copyfile(
                        os.path.join(dir_path, file_name),
                        os.path.join(output_dir_path, file_name),
                    )


    def copy_jinja_file(self, template_path:str, file_name:str, output_dir_path:str, context:dict):
        output_file_name = file_name.replace('.jinja', '')
        template = Environment(
            loader=FileSystemLoader(searchpath=template_path)
        ).get_template(file_name)

        output_contents = template.render(**context)

        if output_file_name.endswith('.py'):
            try:
                output_contents = black.format_str(
                    output_contents,
                    mode=black.FileMode(line_length=80),
                )
            except Exception as exception:
                print(f"Problem processing {output_file_name}")
                raise exception from exception

        with open(os.path.join(output_dir_path, output_file_name), 'w') as output_file: # pylint: disable=W1514
            output_file.write(output_contents)


    def validate_name(self, name: str, name_or_dir='name') -> None:
        """
        Validate Application or project name
        """
        if name is None:
            raise CommandError(
                "you must provide {an} {app} name".format(
                    an=self.a_or_an,
                    app=self.app_or_project_name
                )
            )

        if not name.isidentifier():
            raise CommandError(
                "'{name}' is not a valid {app} {type}. Please make sure the "
                "{type} is valid identifier.".format(
                    name=name,
                    app=self.app_or_project_name,
                    type='name'
                )
            )

        if find_spec(name) is not None and name_or_dir != 'directory':
            raise CommandError(
                "'{name}' conflicts with the name of an existing python "
                "module and cannot be used as {an} {app} {type}. Please try "
                "another {type}.".format(
                    name=name,
                    an=self.a_or_an,
                    app=self.app_or_project_name,
                    type=name_or_dir
                )
            )


    def make_writeable(self, filename):
        """
        Make sure that the file is writeable.
        Useful if our source is read-only.
        """
        if not os.access(filename, os.W_OK):
            st = os.stat(filename)
            new_permissions = stat.S_IMODE(st.st_mode) | stat.S_IWUSR
            os.chmod(filename, new_permissions)


    def snake_case(self, name:str):
        """
        Convert string to snake_case, words must be separate by spaces, to work correctly.
        """
        return name.replace(" ", "_").lower()


    def camel_case(self, name: str):
        """
        Convert String to CamelCase
        """
        return name.replace('_', ' ').title().replace(' ', '')


    def mkdir(self, path):
        """
        Create directory
        """
        if not os.path.exists(path):
            os.mkdir(path)


@click.command()
def shell(env: MigrationEnv) -> None:
    """
    Starts an interactive ipython shell with all the models
    and important python libraries.

    This can be used with a Migration class or with EdgyExtra object lookup.
    """
    try:
        registry = env.app._edgy_db["migrate"].registry  # type: ignore
    except AttributeError:
        registry = env.app._edgy_extra["extra"].registry  # type: ignore

    if (
        sys.platform != "win32"
        and not sys.stdin.isatty()
        and select.select([sys.stdin], [], [], 0)[0]
    ):
        exec(sys.stdin.read(), globals())
        return

    on_startup = getattr(env.app, "on_startup", [])
    on_shutdown = getattr(env.app, "on_shutdown", [])
    lifespan = getattr(env.app, "lifespan", None)
    lifespan = handle_lifespan_events(
        on_startup=on_startup, on_shutdown=on_shutdown, lifespan=lifespan
    )
    execsync(run_shell)(env.app, lifespan, registry)
    return None


async def run_shell(app: Any, lifespan: Any, registry: Registry) -> None:
    """Executes the database shell connection"""

    async with lifespan():
        from edgy.cli.operations.shell.ptpython import get_ptpython

        ptpython = get_ptpython(app=app, registry=registry)
        nest_asyncio.apply()
        ptpython()



@click.option(
    "--schema",
    default=None,
    help=("Database schema to be applied."),
)
@click.command()
def inspect_db(
    schema: str | None = None,
) -> None:
    """
    Inspects an existing database and generates the Edgy reflect models.
    """
    database = os.environ.get("EDGY_DATABASE_URL")
    inspect_db = InspectDB(database=database, schema=schema)
    inspect_db.inspect()
