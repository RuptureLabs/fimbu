from functools import lru_cache
from fimbu.conf import settings
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.db import Database, Registry
from fimbu.db.base import DatabaseRegistry


def get_database(db_settings: dict) -> tuple[str, Database] | None:
    """
    Create database connection
    """
    default_ports = {"postgres": 5432, "mysql": 3306, "mssql": 1433}

    def get_backend_default_port(backend: str) -> int:
        for pb, port in default_ports.items():
            if backend.startswith(pb):
                return port
        raise ImproperlyConfigured(f"Database port is missing for '{backend}'")

    try:
        backend = db_settings["engine"]

        if not backend in Database.SUPPORTED_BACKENDS:
            raise ValueError(f"Unsupported database backend '{db_settings['engine']}'")
        
        if backend == "sqlite":
            db_url = f"sqlite:///{db_settings['database']}"
        else:
            port = db_settings["port"] if 'port' in db_settings else get_backend_default_port(backend)
            db_url = f"{backend}://{db_settings['user']}:{db_settings['password']}@{db_settings['host']}:{port}/{db_settings['database']}"
        
    except KeyError as exc:
        raise ImproperlyConfigured("Invalid database settings") from exc
    return db_settings['database'], Database(db_url)


@lru_cache
def get_db_registry() -> DatabaseRegistry:
    db_settings = getattr(settings, "DATABASES", None)
    db_url = None
    _primary = None
    _dr = DatabaseRegistry()

    if not db_settings:
        _dr['default'] = Database("sqlite:///:memory:")
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
        raise ImproperlyConfigured("Invalid database settings")

    return _dr
    

database_registry = get_db_registry()

@lru_cache()
def get_db_connection():
    database = database_registry.get_primary_db()
    return database, Registry(database=database, extra=database_registry.get_extras())
