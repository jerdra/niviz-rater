from string import Template
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

    db, settings, _ = configured_db
    new_name = "NEW_NAME"

    component = models.Component.get_by_id(1)
    qc_entity = spec.QCEntity(images=[],
                              entities={},
                              tpl_label=Template(new_name),
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


def test_create_or_update_entity_update_if_update_existing(configured_db):
    db, settings, _ = configured_db
    new_name = "NEW_NAME"

    component = models.Component.get_by_id(1)
    qc_entity = spec.QCEntity(images=[],
                              entities={},
                              tpl_label=Template(new_name),
                              tpl_column_name=Template(
                                  settings['column_name']),
                              tpl_row_name=Template(settings['row_name']))

    dbutils.create_or_update_entity(db,
                                    component=component,
                                    qc_entity=qc_entity,
                                    update_existing=True,
                                    reset_on_update=False)

    entity = models.Entity.get_by_id(1)
    expected_rating = models.Rating.get(
        models.Rating.name == settings['rating_name'])
    expected_annotation = models.Annotation.get(
        models.Annotation.name == settings['annotation_name'])

    assert entity.name == new_name
    assert entity.rating == expected_rating
    assert entity.annotation == expected_annotation


def test_create_or_update_entity_update_and_reset_if_both_flags(configured_db):
    db, settings, _ = configured_db
    new_name = "NEW_NAME"

    component = models.Component.get_by_id(1)
    qc_entity = spec.QCEntity(images=[],
                              entities={},
                              tpl_label=Template(new_name),
                              tpl_column_name=Template(
                                  settings['column_name']),
                              tpl_row_name=Template(settings['row_name']))

    dbutils.create_or_update_entity(db,
                                    component=component,
                                    qc_entity=qc_entity,
                                    update_existing=True,
                                    reset_on_update=True)

    entity = models.Entity.get_by_id(1)

    assert entity.name == new_name
    assert entity.rating is None
    assert entity.annotation is None


def component_entities_to_db_correctly_inserts_records(db):

    settings = {"Ratings": ["A", "B", "C"]}
    available_annotations = ["1", "2", "3"]
    component_name = "COMPONENT"
    dbutils.initialize_tables(db, settings=settings)

    images1 = ["path/1a", "path/1b", "path/1c"]
    qc_entity_1 = spec.QCEntity(images=images1,
                                entities={"subject": "001"},
                                tpl_label=Template("${subject}_label"),
                                tpl_column_name=Template("col"),
                                tpl_row_name=Template("${subject}_row"))

    images2 = ["path/2a", "path/2b", "path/2c"]
    qc_entity_2 = spec.QCEntity(images=images2,
                                entities={"subject": "002"},
                                tpl_label=Template("${subject}_label"),
                                tpl_column_name=Template("col"),
                                tpl_row_name=Template("${subject}_row"))

    images3 = ["path/3a", "path/3b", "path/3c"]
    qc_entity_3 = spec.QCEntity(images=images3,
                                entities={"subject": "003"},
                                tpl_label=Template("${subject}_label"),
                                tpl_column_name=Template("col"),
                                tpl_row_name=Template("${subject}_row"))

    qc_entities = [qc_entity_1, qc_entity_2, qc_entity_3]
    component_entities = spec.ComponentEntities(
        component_name=component_name,
        available_annotations=available_annotations,
        entities=qc_entities)

    dbutils.component_entities_to_db(db, component_entities)

    # Test whether we have expected resulting table
    assert models.Component.get_or_none(
        models.Component.name == component_name) is not None

    # Test that we have the correct number of entities
    assert len(models.Entity.select()) == 3

    # Test to make sure we have 3 row/column combinations
    assert len(models.TableRow.select()) == 3
    assert len(models.TableColumn.select()) == 1

    # Make sure we have right number of images
    assert len(models.Image.select()) == 9

    # Make sure that component has right number of available annotations
    annotations = models.Annotation \
        .select(models.Annotation, models.Component) \
        .join(models.Component) \
        .where(models.Component.name == component_name)
    assert len(annotations) == 3
