from string import Template

from peewee import SqliteDatabase
from typing import Any, List, Optional, Dict

from niviz_rater.index import make_database, ConfigComponent, AxisNameTpl

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


def build_index(db: SqliteDatabase,
                bids_files: List[str],
                qc_spec: Dict[str, Any]) -> None:
    """
    Initialize database with objects
    """
    row_tpl = AxisNameTpl(Template(qc_spec['RowDescription']['name']),
                          qc_spec['RowDescription']['entities'])

    for c in qc_spec['Components']:
        component = ConfigComponent(**c)
        make_database(db,
                      component.build_qc_entities(bids_files),
                      component.available_ratings,
                      row_tpl)
