from functools import lru_cache
from fimbu.conf import settings
from fimbu.core.exceptions import ImproperlyConfigured
from fimbu.db import Database, Registry


@lru_cache
def build_db_url():
    db_settings = getattr(settings, "DATABASES", None)
    db_url = None

    if not db_settings:
        return "sqlite:///:memory:" 
    
    try:
        if db_settings["engine"] == "sqlite":
            db_url = f"sqlite:///{db_settings['database']}"
        elif db_settings["engine"] == "postgresql":
            port = db_settings["port"] if 'port' in db_settings else 5432
            db_url = f"postgresql+asyncpg://{db_settings['user']}:{db_settings['password']}@{db_settings['host']}:{port}/{db_settings['database']}"
        elif db_settings["engine"] == "mysql":
            port = db_settings["port"] if 'port' in db_settings else 3306
            db_url = f"mysql://{db_settings['user']}:{db_settings['password']}@{db_settings['host']}:{port}/{db_settings['database']}"
        else:
            raise ValueError(f"Unsupported database engine '{db_settings['engine']}'")
    except KeyError as exc:
        raise ImproperlyConfigured("Invalid database settings") from exc
    return db_url


@lru_cache
def get_database():
    database = Database(build_db_url())
    return database


@lru_cache()
def get_db_connection():
    database = get_database()
    return database, Registry(database=database)
