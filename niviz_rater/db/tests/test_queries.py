import niviz_rater.db.queries as queries
import niviz_rater.db.models as models


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


def test_denormalized_entities_returns_fully_populated_models(configured_db):

    db, settings, foreign_keys = configured_db
