from peewee import SqliteDatabase
from typing import Any, List, Optional, Dict
import niviz_rater.models as models


def get_or_create_db(
        db_str: str,
        additional_pragmas: Optional[List[Any]] = None) -> SqliteDatabase:

    pragmas = [('foreign_keys', 'on')]
    if additional_pragmas:
        pragmas.append(additional_pragmas)

    sqlite_db = SqliteDatabase(db_str, pragmas=pragmas, uri=True)
    return sqlite_db


def fetch_db_from_config(app_config,
                         additional_pragmas: Optional[List[Any]] = None):
    """
    Fetch database by first trying to pull from
    stored application configuration and if fail, then
    resort to requesting one using db_file
    """

    return app_config.get(
        'niviz_rater.db.instance',
        get_or_create_db(app_config['niviz_rater.db.file'],
                         additional_pragmas))


def initialize_tables(db: SqliteDatabase,
                      settings: Dict[str, Any]) -> SqliteDatabase:
    """
    Initialize the Niviz database table with a given
    set of settings
    """

    db.create_tables([
        models.Component, models.Annotation, models.Rating, models.TableColumn,
        models.TableRow, models.Entity, models.Image
    ])

    # Pre-construct the Ratings table
    with db.atomic():
        models.Rating.create(name=settings["DefaultRating"])
        [models.Rating.create(name=r) for r in settings["Ratings"]]

    return db
