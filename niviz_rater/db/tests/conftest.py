import pytest
from peewee import SqliteDatabase
from niviz_rater.db.models import database_proxy
import niviz_rater.db.models as models

DB = SqliteDatabase(":memory:")
database_proxy.initialize(DB)

MODELS = [
    models.Rating, models.Component, models.Entity, models.Image,
    models.TableRow, models.TableColumn, models.Annotation
]


@pytest.fixture
def db():
    """
    Provide fresh DB session
    """
    DB.connect()
    yield DB

    DB.drop_tables(MODELS)
    DB.close()
