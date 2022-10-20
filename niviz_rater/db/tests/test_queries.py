import niviz_rater.db.queries as queries
import niviz_rater.db.models as models
from playhouse.test_utils import count_queries


def _create_entity_column(name, columnname, foreign_keys, rating=None):

    tc = models.TableColumn(name=columnname)
    tc.save()
    return models.Entity.create(name=name,
                                columnname=tc,
                                rating=rating,
                                **foreign_keys)


def test_summary_returns_correct_number_of_entities(configured_db):
    """
    Correct number of rated, unrated, and total number of entities
    is returned by get_summary()
    """

    db, settings, foreign_keys = configured_db
    _create_entity_column("anentity", "acolumnname", foreign_keys)
    rating = models.Rating.get_by_id(1)
    _create_entity_column("anotherentity", "anothercolumnname", foreign_keys,
                          rating)

    total, n_rated, n_unrated = queries.get_summary()

    assert total == 3
    assert n_rated == 2
    assert n_unrated == 1


def test_denormalized_entities_returns_fully_denormalied_models(configured_db):
    """
    Ensure that fully denormalized entities are returned,
    additional queries should not be executed when inspecting
    relationships
    """

    db, settings, foreign_keys = configured_db

    e1 = models.Entity.get_by_id(1)
    e2 = _create_entity_column("anentity", "acolumnname", foreign_keys)
    rating = models.Rating.get_by_id(1)
    e3 = _create_entity_column("anotherentity", "anothercolumnname",
                               foreign_keys, rating)

    results = queries.get_denormalized_entities()
    assert set(results) == set([e1, e2, e3])

    # No additional queries should be made (data is fully denormalized)
    with count_queries() as counter:
        for entity in results:

            entity.component.name
            entity.rowname.name
            entity.columnname.name

            if entity.annotation:
                entity.annotation.name

            if entity.rating:
                entity.rating.name

            [i.path for i in entity.images]

    assert counter.count == 0


def test_get_denormalized_by_id_returns_fully_populated_entity(configured_db):

    db, settings, foreign_keys = configured_db

    e2 = _create_entity_column("anentity", "acolumnname", foreign_keys)
    rating = models.Rating.get_by_id(1)
    _create_entity_column("anotherentity", "anothercolumnname", foreign_keys,
                          rating)

    result = queries.get_denormalized_entity_by_id(2)
    assert e2 == result

    with count_queries() as counter:
        result.component.name
        result.rowname.name
        result.columnname.name

        if result.annotation:
            result.annotation.name

        if result.rating:
            result.rating.name

        [i.path for i in result.images]

    assert counter.count == 0


def test_get_available_annotations(configured_db):

    db, settings, foreign_keys = configured_db
    entity = models.Entity.get_by_id(1)
    annotation_names = [
        a.name for a in queries.get_available_annotations(entity)
    ]

    expected_names = settings["available_annotations"]
    assert set(expected_names) == set(annotation_names)


def test_get_denormalized_table_rows(configured_db):

    db, settings, foreign_keys = configured_db

    _create_entity_column("anentity", "acolumn", foreign_keys)
    _create_entity_column("anotherentity", "anothercolumn", foreign_keys)

    new_row_key = models.TableRow.create(name="anotherrow")
    new_row_key.save()
    new_row_fkey = {"component": foreign_keys["component"], **foreign_keys}
    _create_entity_column("newrowentity", "acolumn", new_row_fkey)
    _create_entity_column("anothernewrowentity", "anothercolumn", new_row_fkey)

    results = queries.get_denormalized_rows()
    expected_rows = [foreign_keys["rowname"], new_row_key]
    assert set(results) == set(expected_rows)

    # Check denormalized
    with count_queries() as counter:
        for row in results:
            for entity in row.entities:
                entity.component.name
                entity.columnname.name
                if entity.rating:
                    entity.rating.name
                if entity.annotation:
                    entity.annotation.name

    assert counter.count == 0

def test_get_table_columns_returns_ordered_columns(db):


    db.create_tables(models.DB_TABLES)
    tc1 = models.TableColumn.create(name="a")
    tc3 = models.TableColumn.create(name="c")
    tc2 = models.TableColumn.create(name="b")

    result = queries.get_columns()

    assert len(result) == 3
    for result, expect in zip(result, [tc1, tc2, tc3]):
        assert result == expect
