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
                             reset_state: bool = False):
    """
    Add component with entities to DB, skip adding existing components

    Options:
        update_existing: Causes already existing entities to be updated
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
            logger.info("Creating new entity\n"
                        f"Row: {entity.rowname}\n"
                        f"Column: {entity.column_name}")
            entity_model = models.Entity(name=entity.name,
                                         component=component,
                                         rowname=entity.rowname,
                                         columnname=entity.columnname)

        elif update_existing:
            logger.info("Updating existing Entity\n"
                        f"Row: {entity.rowname}\n"
                        f"Column: {entity.column_name}\n")

            # We delete images to respect new order
            # TODO: Have order be explicitly represented in DB
            images = entity_model.images
            logger.info("Setting QC images for Entity...")
            with db.atomic():
                [image.delete() for image in images]

            entity_model.name = entity.name

            if reset_state:
                logger.info("`reset_state` set!\n"
                            "Undoing QC for Entity")
                entity_model.annotation = None
                entity_model.rating = None

        # Save updates/creation
        with db.atomic():
            entity_model.save()

        for image in entity.images:
            entity_model.add_image(image)

        logger.info("Successfully committed Entity to DB")
