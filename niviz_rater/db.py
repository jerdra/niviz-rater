from peewee import SqliteDatabase
from typing import Any, List, Optional

# As much as it would be nice to have this be passed into the app via a
# configuration file, but peewee Models are not compatible with this
# To use an in-memory db, use 'file::memory:?cache=shared'
DB_NAME: str = 'test.db'

sqlite_db: Optional[SqliteDatabase] = None


def get_or_create_db(additional_pragmas: Optional[List[Any]] = None
                     ) -> SqliteDatabase:
    global sqlite_db
    if sqlite_db:
        return sqlite_db
    pragmas = [('foreign_keys', 'on')]
    if additional_pragmas:
        pragmas.append(additional_pragmas)
    sqlite_db = SqliteDatabase(DB_NAME, pragmas=pragmas, uri=True)
    return sqlite_db

