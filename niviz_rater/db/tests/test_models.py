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


def test_entity_entry_formatted_correctly(db):

    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    expected_entry = (annotation_name, rating_name, comment)
    assert entity.entry == expected_entry


def test_entity_add_image_updates_db(db):

    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    image_path = Path("/this/is/a/path")
    with db.atomic():
        entity.add_image(image_path)

    img = models.Image.get((models.Image.path == str(image_path))
                           & (models.Image.entity == entity))

    assert img.path == str(image_path)
    assert img.entity == entity


def test_adding_same_image_to_entity_returns_same_image(db):

    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    image_path = Path("/this/is/a/path")
    with db.atomic():
        image1 = entity.add_image(image_path)
        image2 = entity.add_image(image_path)

    assert image1 == image2


def test_entity_update_annotation_sets_correctly_if_configured(db):

    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    # Add new annotation
    new_annotation_name = "new annotation"
    with db.atomic():
        # Add annotation, store model instance
        new_annotation = component.add_annotation(new_annotation_name)

        # Update annotation using just name
        entity.update_annotation(new_annotation_name)

    #
    assert entity.annotation == new_annotation


def test_entity_update_annotation_creates_if_flag_set(db):

    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    # Add new annotation
    new_annotation_name = "new annotation"
    with db.atomic():

        # Update annotation using just name
        entity.update_annotation(new_annotation_name, create=True)

    assert entity.annotation.name == new_annotation_name


def test_entity_update_annotation_does_nothing_if_flag_not_set(db):

    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    # Add new annotation
    new_annotation_name = "new annotation"
    with db.atomic():

        # Update annotation using just name, this should do nothing
        entity.update_annotation(new_annotation_name, create=False)

    assert entity.annotation == annotation


def test_entity_update_rating_sets_if_rating_exists(db):
    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)
    # Get rating
    new_rating = models.Rating.get(models.Rating.name == "B")

    with db.atomic():
        entity.update_rating(new_rating.name)

    assert entity.rating == new_rating


def test_entity_update_rating_does_nothing_if_rating_invalid(db):
    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)
    # Get rating
    with db.atomic():
        entity.update_rating("FAKE")

    assert entity.rating == rating


def test_set_images_fully_replaces_images(db):
    annotation_name = "12345"
    rating_name = "A"
    comment = "A COMMENT"
    settings = {"Ratings": ["A", "B", "C", "D"]}

    db = dbutils.initialize_tables(db, settings)

    # Set up required Foreign Keys
    tr = models.TableRow(name="row")
    tc = models.TableColumn(name="column")
    component = models.Component(name="abc")
    with db.atomic():
        tr.save()
        tc.save()
        component.save()
        annotation = component.add_annotation(annotation_name)
    rating = models.Rating.get(models.Rating.name == rating_name)

    # Create Entity
    entity = models.Entity.create(name="111",
                                  columnname=tc,
                                  rowname=tr,
                                  component=component,
                                  comment=comment,
                                  rating=rating,
                                  annotation=annotation)

    old_images = [Path(i) for i in ["/a/", "/b/", "/c/"]]
    [entity.add_image(i) for i in old_images]

    new_images = [Path(i) for i in ["/e/", "/k/", "/a/"]]
    entity.set_images(new_images)

    for img, expect_img in zip(entity.images, new_images):
        assert Path(img.path) == expect_img
