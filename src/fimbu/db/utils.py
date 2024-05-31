from __future__ import annotations

from typing import TYPE_CHECKING, Any, cast
from functools import lru_cache
from urllib.parse import urlencode
from copy import copy
from fimbu.conf import settings
from sqlalchemy.orm import InstrumentedAttribute
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.db import Database, Registry
from fimbu.db.base import DatabaseRegistry
from fimbu.core.types import ModelT


if TYPE_CHECKING:
    from sqlalchemy.orm import InstrumentedAttribute

    from fimbu.core.types import ModelProtocol


def get_database(db_settings: dict) -> tuple[str, Database] | None:
    """
    Create database object
    """
    default_ports = {"postgres": 5432, "mysql": 3306, "mssql": 1433}
    supported_backends = copy(Database.SUPPORTED_BACKENDS)
    supported_backends.update({'postgresql+asyncpg' : 'databasez.backends.aiopg:PostgresBackend'})

    def get_backend_default_port(backend: str) -> int:
        for pb, port in default_ports.items():
            if backend.startswith(pb):
                return port
        raise ImproperlyConfigured(f"Database port is missing for '{backend}'")

    try:
        backend: str = db_settings["engine"]

        if not backend in supported_backends:
            raise ValueError(f"Unsupported database backend '{db_settings['engine']}'")
        
        if backend.startswith("sqlite"):
            db_url = f"{backend}:///{db_settings['database']}"
        else:
            port = db_settings["port"] if 'port' in db_settings else get_backend_default_port(backend)
            db_url = f"{backend}://{db_settings['user']}:{db_settings['password']}@{db_settings['host']}:{port}/{db_settings['database']}"

        if 'options' in db_settings:
            db_url += f"?{urlencode(db_settings['options'])}"
        
    except KeyError as exc:
        raise ImproperlyConfigured(f"Invalid database settings {exc}") from exc
    return db_settings['database'], Database(db_url)


@lru_cache
def get_db_registry() -> DatabaseRegistry:
    db_settings = getattr(settings, "DATABASES", None)
    _primary = None
    _dr = DatabaseRegistry()

    if not db_settings and settings.USE_IN_MEMORY_DATABASE:
        url = "sqlite:///:memory:"

        try:
            import aiosqlite
            url = "sqlite+aiosqlite:///:memory:"
        except:
            pass

        _dr['default'] = Database(url)
        _dr.set_primary_db('default')

        return _dr
    
    if isinstance(db_settings, dict):
        name, db = get_database(db_settings)
        _dr[name] = db
        _dr.set_primary_db(name)
    
    elif isinstance(db_settings, (list, tuple)):
        for db in db_settings:
            name, _db = get_database(db)
            _dr[name] = _db

            if 'primary' in db and not _primary:
                _primary = name

        if not _primary:
            _dr.set_primary_db(db_settings[0]['database'])
        else:
            _dr.set_primary_db(_primary)
    else:
        raise ImproperlyConfigured("Invalid database settings")

    return _dr


@lru_cache()
def get_db_connection():
    database_registry = get_db_registry()
    database = database_registry.get_primary_db()
    return database, Registry(database=database, extra=database_registry.get_extras())


def get_instrumented_attr(model: type[ModelProtocol], key: str | InstrumentedAttribute) -> InstrumentedAttribute:
    if isinstance(key, str):
        return cast("InstrumentedAttribute", getattr(model.columns, key))
    return key

