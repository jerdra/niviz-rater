import pytest
from peewee import SqliteDatabase
from niviz_rater.db.models import database_proxy
import niviz_rater.db.models as models
import niviz_rater.db.utils as dbutils

DB = SqliteDatabase(":memory:", pragmas={'foreign_keys': 1})
database_proxy.initialize(DB)


@pytest.fixture
def db():
    """
    Provide fresh DB session
    """
    DB.connect()
    yield DB

    DB.drop_tables(models.DB_TABLES)
    DB.close()


@pytest.fixture
def settings():
    return {
        "annotation_name": "12345",
        "available_annotations": ["12345", "ABCDEFG", "QWERTY"],
        "rating_name": "A",
        "comment": "A COMMENT",
        "settings": {
            "Ratings": ["A", "B", "C", "D"]
        },
        "row_name": "row",
        "column_name": "column",
        "component_name": "abc",
        "entity_name": "111"
    }


def configure_db(db, annotation_name, available_annotations, rating_name,
                 comment, settings, column_name, row_name, component_name,
                 entity_name):

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name=row_name)
    tc = models.TableColumn(name=column_name)
    component = models.Component(name=component_name)
    with db.atomic():
        tr.save()
        tc.save()
        component.save()

        for annotation in available_annotations:
            component.add_annotation(annotation)



    rating = models.Rating.get(models.Rating.name == rating_name)

    annotation = models.Annotation.get(
        models.Annotation.name == annotation_name)

    # Create Entity
    models.Entity.create(name=entity_name,
                         columnname=tc,
                         rowname=tr,
                         component=component,
                         comment=comment,
                         rating=rating,
                         annotation=annotation)
    foreign_keys = {"rowname": tr, "component": component}

    return foreign_keys


@pytest.fixture
def configured_db(db, settings):
    foreign_keys = configure_db(db, **settings)
    return db, settings, foreign_keys
