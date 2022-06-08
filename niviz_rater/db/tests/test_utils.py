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
    default_rating = "C"
    settings = {"DefaultRating": default_rating, "Rating": expected_ratings}
    dbutils.initialize_tables(db, settings)

    found_ratings = [r.name for r in models.Rating]
    assert set(expected_ratings) == set(found_ratings)

    found_default = models.Rating.get(
        models.Rating.is_default == True)  # noqa: E712
    assert default_rating == found_default.name
