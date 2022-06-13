from __future__ import annotations
from typing import Any, List, Optional, TYPE_CHECKING
import logging
from peewee import SqliteDatabase
import niviz_rater.db.models as models
import niviz_rater.db.exceptions as exceptions
import niviz_rater.config.db_defaults as db_defaults
import niviz_rater.db.queries as queries
from niviz_rater.spec import DBSettings

if TYPE_CHECKING:
    from niviz_rater.spec import ComponentEntities

logger = logging.getLogger(__name__)


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


def add_ratings(db: SqliteDatabase, settings: DBSettings) -> SqliteDatabase:

    if 'Ratings' not in settings:
        ratings = db_defaults.RATINGS
    else:
        ratings = settings['Ratings']

    with db.atomic():
        for rating in ratings:
            models.Rating.get_or_create(name=rating)

    return db


def is_initialized(db: SqliteDatabase):
    return set(db.get_tables()) == set(models.DB_TABLE_NAMES)


def initialize_tables(db: SqliteDatabase,
                      settings: DBSettings) -> SqliteDatabase:
    """
    Initialize the Niviz database table with a given
    set of settings
    """

    # Check if tables already initialized
    if is_initialized(db):
        raise exceptions.IsInitialized

    db.create_tables(models.DB_TABLES)
    db = add_ratings(db, settings)

    return db


def component_entities_to_db(db: SqliteDatabase,
                             component_entities: ComponentEntities,
                             update_existing: bool = False,
                             reset_on_update: bool = True):
    """
    Add component with entities to DB, skip adding existing components

    Options:
        update_existing: Causes already existing entities to be updated
        reset_on_update: Undo an existing entity's QC rating
    """

    # Create component
    component: models.Component = models.Component.get_or_create(
        name=component_entities.component_name)

    # Add annotations for component
    for annotation in component_entities.available_annotations:
        component.add_annotation(annotation)

    # Add Row names and Column names
    with db.atomic():
        for row in component_entities.rows:
            models.TableRow.get_or_create(name=row)

    with db.atomic():
        for column in component_entities.columns:
            models.TableColumn.get_or_create(name=column)

    for entity in component_entities.entities:

        entity_model = queries.get_entity_by_row_col(entity.rowname,
                                                     entity.column_name)

        if entity_model is None:
            logger.info(f"Creating new Entity\n {entity_model}")
            entity_model = models.Entity(name=entity.name,
                                         component=component,
                                         rowname=entity.rowname,
                                         columnname=entity.columnname)
            entity_model.save()
            entity_model.set_images(entity.images)

        elif update_existing:
            logger.info(f"Updating existing Entity\n {entity_model}")

            entity_model.set_images(entity.images)
            entity_model.name = entity.name

            if reset_on_update:
                logger.info("`reset_on_update` set!\n"
                            "Undoing QC for Entity")
                entity_model.remove_qc()
        else:
            logger.info("Skipping update to Entity\n {entity_model}")
            return

        logger.info("Successfully committed Entity to DB")
        return
