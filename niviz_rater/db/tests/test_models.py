from pathlib import Path

import niviz_rater.db.models as models
import niviz_rater.db.utils as dbutils


def test_component_add_annotation_updates_db(db):
    """
    When annotation is added to component, make sure it is
    added to database
    """
    db.create_tables([models.Component, models.Annotation])

    annot_name = "12345"
    with db.atomic():
        component = models.Component(name="TEST")
        component.save()
        component.add_annotation(annot_name)

    result = models.Annotation.get(models.Annotation.name == annot_name)

    assert result.name == annot_name
    assert result.component == component


def test_component_add_annotation_does_not_create_when_already_exists(db):
    """
    When annotation is already available in Component, make sure a duplicate
    is not added
    """

    db.create_tables([models.Component, models.Annotation])

    annot_name = "12345"
    with db.atomic():
        component = models.Component(name="TEST")
        component.save()
        annot1 = component.add_annotation(annot_name)
        annot2 = component.add_annotation(annot_name)

    assert annot1 == annot2


def test_entity_entry_formatted_correctly(configured_db):

    db, settings, _ = configured_db

    annotation_name = settings['annotation_name']
    rating_name = settings['rating_name']
    comment = settings['comment']

    entity = models.Entity.get_by_id(1)

    expected_entry = (annotation_name, rating_name, comment)
    assert entity.entry == expected_entry


def test_entity_add_image_updates_db(configured_db):

    db, settings, _ = configured_db

    entity = models.Entity.get_by_id(1)
    image_path = Path("/this/is/a/path")
    with db.atomic():
        entity.add_image(image_path)

    img = models.Image.get((models.Image.path == str(image_path))
                           & (models.Image.entity == entity))

    assert img.path == str(image_path)
    assert img.entity == entity


def test_adding_same_image_to_entity_returns_same_image(configured_db):

    db, settings, _ = configured_db

    entity = models.Entity.get_by_id(1)
    image_path = Path("/this/is/a/path")
    with db.atomic():
        image1 = entity.add_image(image_path)
        image2 = entity.add_image(image_path)

    assert image1 == image2


def test_entity_update_annotation_sets_correctly_if_configured(configured_db):

    db, settings, _ = configured_db

    entity = models.Entity.get_by_id(1)
    component = models.Component.get_by_id(1)

    new_annotation_name = "new annotation"
    with db.atomic():
        # Add annotation, store model instance
        new_annotation = component.add_annotation(new_annotation_name)

        # Update annotation using just name
        entity.update_annotation(new_annotation_name)

    assert entity.annotation == new_annotation


def test_entity_update_annotation_creates_if_flag_set(configured_db):

    db, settings, _ = configured_db
    entity = models.Entity.get_by_id(1)

    # Add new annotation
    new_annotation_name = "new annotation"
    with db.atomic():

        # Update annotation using just name
        entity.update_annotation(new_annotation_name, create=True)

    assert entity.annotation.name == new_annotation_name


def test_entity_update_annotation_does_nothing_if_flag_not_set(configured_db):

    db, settings, _ = configured_db
    entity = models.Entity.get_by_id(1)

    # Add new annotation
    new_annotation_name = "new annotation"
    with db.atomic():

        # Update annotation using just name, this should do nothing
        entity.update_annotation(new_annotation_name, create=False)

    annotation = models.Annotation.get(
        models.Annotation.name == settings['annotation_name'])
    assert entity.annotation == annotation


def test_entity_update_rating_sets_if_rating_exists(configured_db):

    db, settings, _ = configured_db

    entity = models.Entity.get_by_id(1)

    # Get rating
    new_rating = models.Rating.get(models.Rating.name == "B")

    with db.atomic():
        entity.update_rating(new_rating.name)

    assert entity.rating == new_rating


def test_entity_update_rating_does_nothing_if_rating_invalid(configured_db):

    db, settings, _ = configured_db
    entity = models.Entity.get_by_id(1)
    rating = models.Rating.get(models.Rating.name == settings['rating_name'])

    # Get rating
    with db.atomic():
        entity.update_rating("FAKE")

    assert entity.rating == rating


def test_set_images_fully_replaces_images(configured_db):

    db, settings, _ = configured_db
    entity = models.Entity.get_by_id(1)

    old_images = [Path(i) for i in ["/a/", "/b/", "/c/"]]
    [entity.add_image(i) for i in old_images]

    new_images = [Path(i) for i in ["/e/", "/k/", "/a/"]]
    entity.set_images(new_images)

    for img, expect_img in zip(entity.images, new_images):
        assert Path(img.path) == expect_img
