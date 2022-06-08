import pytest
from peewee import SqliteDatabase
from niviz_rater.db.models import database_proxy

DB = SqliteDatabase(":memory:")
database_proxy.initialize(DB)


@pytest.fixture
def db():
    """
    Provide fresh DB session
    """
    DB.connect()
    yield DB
    DB.close()
