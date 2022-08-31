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


def test_get_available_annotations(configured_db):

    db, settings, foreign_keys = configured_db
    entity = models.Entity.get_by_id(1)
    annotation_names = [
        a.name for a in queries.get_available_annotations(entity)
    ]

    expected_names = settings["available_annotations"]
    assert set(expected_names) == set(annotation_names)
