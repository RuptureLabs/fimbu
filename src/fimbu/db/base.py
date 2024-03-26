

from edgy import Database
from .exceptions import DatabaseNotFound


class DatabaseRegistry:
    def __init__(self) -> None:
        """
        Database registry
        """
        self._primary_db : str | None = None
        self._databases: dict[str, Database] = {}


    def __setitem__(self, key: str, value: Database):
        self._databases[key] = value


    def __getitem__(self, key):
        if key not in self._databases:
            raise DatabaseNotFound(f"Database '{key}' not found")
        return self._databases[key]


    def get_primary_db(self) -> Database | None:
        """
        Get primary database
        """
        if self._databases:
            return self._databases[self._primary_db]
        return None
    

    def get_extras(self) -> dict[str, Database]:
        """
        Get all databases except primary one
        """
        _d = {}
        for  k, v in self._databases.items():
            if k != self._primary_db:
                _d[k] = v
        return _d

    
    def set_primary_db(self, name:str) -> None:
        """
        Set primary database
        """
        if name not in self._databases:
            raise DatabaseNotFound(f"Database '{name}' not found")
        self._primary_db = name
