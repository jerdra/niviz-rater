from unittest.mock import patch
from peewee import SqliteDatabase
from string import Template
from niviz_rater.db.models import database_proxy
import niviz_rater.db.models as models
import niviz_rater.db.utils as dbutils
import niviz_rater.spec as spec


def test_ratings_are_initialized_with_settings(db):
    """
    Ensure Ratings are created according to the settings provided
    """

    expected_ratings = ["A", "B", "C", "D"]
    settings = {"Ratings": expected_ratings}
    dbutils.initialize_tables(db, settings)

    found_ratings = [r.name for r in models.Rating]
    assert set(expected_ratings) == set(found_ratings)


def test_create_or_update_entity_skips_update_if_flag_not_set(configured_db):

    db, settings = configured_db
    new_name = "NEW_NAME"

    tablerow = models.TableRow.get_by_id(1)
    tablecol = models.TableColumn.get_by_id(1)
    component = models.Component.get_by_id(1)
    qc_entity = spec.QCEntity(images=[],
                              entities={},
                              tpl_label="NEW_NAME",
                              tpl_column_name=Template(
                                  settings['column_name']),
                              tpl_row_name=Template(settings['row_name']))

    dbutils.create_or_update_entity(db,
                                    component=component,
                                    qc_entity=qc_entity)

    entity = models.Entity.get_by_id(1)
    expected_rating = models.Rating.get(
        models.Rating.name == settings['rating_name'])
    expected_annotation = models.Annotation.get(
        models.Annotation.name == settings['annotation_name'])

    assert entity.name == settings['entity_name']
    assert entity.rating == expected_rating
    assert entity.annotation == expected_annotation


def test_create_or_update_entity_update_if_update_existing(db):
    assert False


def test_create_or_update_entity_update_and_reset_if_both_flags(db):
    assert False


def test_create_or_update_entity_update_does_nothing_if_existing_no_flags(db):
    assert False
