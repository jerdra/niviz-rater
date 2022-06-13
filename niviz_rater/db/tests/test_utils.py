from unittest.mock import patch
from peewee import SqliteDatabase
from niviz_rater.db.models import database_proxy
import niviz_rater.db.models as models
import niviz_rater.db.utils as dbutils

# Use in-memory DB for testing purposes
DB = SqliteDatabase(":memory:")
database_proxy.initialize(DB)


def test_ratings_are_initialized_with_settings(db):
    """
    Ensure Ratings are created according to the settings provided
    """

    expected_ratings = ["A", "B", "C", "D"]
    settings = {"Ratings": expected_ratings}
    dbutils.initialize_tables(db, settings)

    found_ratings = [r.name for r in models.Rating]
    assert set(expected_ratings) == set(found_ratings)


def test_create_or_update_entity_skips_update_if_flag_not_set(db):
    assert False


def test_create_or_update_entity_update_if_update_existing(db):
    assert False


def test_create_or_update_entity_update_and_reset_if_both_flags(db):
    assert False


def test_create_or_update_entity_update_does_nothing_if_existing_no_flags(db):
    assert False
