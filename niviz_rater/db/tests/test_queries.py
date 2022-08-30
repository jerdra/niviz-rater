import niviz_rater.db.queries as queries
import niviz_rater.db.models as models


def test_summary_returns_correct_number_of_entities(configured_db):
    """
    Correct number of rated, unrated, and total number of entities
    is returned by get_summary()
    """

    db, settings, foreign_keys = configured_db

    tc1 = models.TableColumn(name="acolumnname")
    tc2 = models.TableColumn(name="anothercolumnname")
    with db.atomic():
        tc1.save()
        tc2.save()

    models.Entity.create(name="anentity",
                         columnname=tc1,
                         rowname=foreign_keys["rowname"],
                         component=foreign_keys["component"])

    a_rating = models.Rating.get_by_id(1)
    models.Entity.create(name="anentity",
                         columnname=tc2,
                         rowname=foreign_keys["rowname"],
                         component=foreign_keys["component"],
                         rating=a_rating)

    total, n_rated, n_unrated = queries.get_summary()

    assert total == 3
    assert n_rated == 2
    assert n_unrated == 1
