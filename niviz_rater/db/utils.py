from peewee import SqliteDatabase
from typing import Any, List, Optional
import niviz_rater.db.models as models
import niviz_rater.config.db_defaults as db_defaults
from niviz_rater.spec import DBSettings


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


def _create_ratings(db: SqliteDatabase,
                    settings: DBSettings) -> SqliteDatabase:

    if 'Ratings' not in settings:
        ratings = db_defaults.RATINGS
    else:
        ratings = settings['Ratings']

    with db.atomic():
        for rating in ratings:
            models.Rating.create(name=rating)

    return db


def initialize_tables(db: SqliteDatabase,
                      settings: DBSettings) -> SqliteDatabase:
    """
    Initialize the Niviz database table with a given
    set of settings
    """

    db.create_tables([
        models.Component, models.Annotation, models.Rating, models.TableColumn,
        models.TableRow, models.Entity, models.Image
    ])

    db = _create_ratings(db, settings)

    return db
