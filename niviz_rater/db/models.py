"""
Niviz Data Models
"""

from __future__ import annotations
from pathlib import Path
from typing import Union, List, TYPE_CHECKING
import logging
from peewee import (Model, ForeignKeyField, TextField, CharField,
                    DatabaseProxy, IntegrityError, SqliteDatabase)

if TYPE_CHECKING:
    from niviz_rater.spec import QCEntity

logger = logging.getLogger(__name__)

database_proxy = DatabaseProxy()


class BaseModel(Model):

    class Meta:
        database = database_proxy

    @property
    def db(self):
        return self._meta.database


class Component(BaseModel):
    '''
    Component component ID
    '''

    name = CharField(unique=True)

    def add_annotation(self, annotation_name: str) -> Annotation:
        """
        Add an annotation to a component
        """

        annotation = Annotation(name=annotation_name, component=self)
        try:
            with self.db.atomic():
                annotation.save()
        except IntegrityError:
            logger.info(f"Annotation {annotation_name} already exists for "
                        f"component {self.name}!")
            logger.info("Skipping creation...")
            intended_annot = Annotation.get(
                (Annotation.component == self)
                & (Annotation.name == annotation_name))
            return intended_annot

        return annotation


class Annotation(BaseModel):
    '''
    Annotation ID --> named rating mapping
    '''
    name = CharField()
    component = ForeignKeyField(Component, null=False, backref='annotations')

    class Meta:
        database = database_proxy

        # Unique constraint on name-component tuples
        indexes = ((("name", "component"), True), )


class Rating(BaseModel):
    '''
    Pass/Fail/Uncertain/None ratings
    '''
    name = CharField(unique=True)


class TableColumn(BaseModel):
    name = CharField()


class TableRow(BaseModel):
    name = CharField()


class Entity(BaseModel):
    '''
    Single entity to QC
    '''
    name = CharField()
    columnname = ForeignKeyField(TableColumn, null=False, backref='entities')
    rowname = ForeignKeyField(TableRow, null=False, backref='entities')
    component = ForeignKeyField(Component, null=False, backref='entities')
    comment = TextField(default="")
    rating = ForeignKeyField(Rating, null=True)
    annotation = ForeignKeyField(Annotation, null=True)

    class Meta:
        database = database_proxy
        indexes = ((("columnname", "rowname"), True), )

    @classmethod
    def from_qc_entity(cls, db: SqliteDatabase, qc_entity: QCEntity,
                       component: Component) -> Entity:
        """
        Create an Entity model from a QCEntity description
        of an object
        """

        try:
            row = TableRow.get(TableRow.name == qc_entity.row_name)
            col = TableColumn.get(TableColumn.name == qc_entity.column_name)
        except TableRow.DoesNotExist as e:
            logger.error(
                "Tried to create Entity with row name: {qc_entity.row_name}\n"
                "but TableRow does not exist!")
            logger.error(f"Error info: {e}")
            raise
        except TableColumn.DoesNotExist as e:
            logger.error("Tried to create Entity with column name: "
                         " {qc_entity.column_name}\n"
                         "but TableColumn does not exist!")
            logger.error(f"Error info: {e}")
            raise

        with db.atomic():
            entity = cls.create(name=qc_entity.name,
                                component=component,
                                rowname=row,
                                columnname=col)
            entity.set_images(qc_entity.images)
        return entity

    def __repr__(self):
        return (f"Name:  {self.name}\n"
                f"Row: {self.rowname}\n"
                f"Column: {self.columnname}")

    @property
    def entry(self):
        if self.annotation:
            annotation = self.annotation.name
        else:
            annotation = ""

        if self.rating.name == "None":
            rating = ""
        else:
            rating = self.rating.name

        return (annotation, rating, self.comment or "")

    def add_image(self, image_path: Path) -> Image:
        """
        Add image to Entity
        """
        image = Image(path=str(image_path), entity=self)
        try:
            with self.db.atomic():
                image.save()
        except IntegrityError:
            logger.error(f"Image { image_path } is already being used for"
                         f" the Entity { self.name }")
            intended_image = Image.get((Image.path == str(image_path))
                                       & (Image.entity == self))
            return intended_image

        return image

    def update_annotation(self,
                          annotation: Union[str, Annotation],
                          create=False):
        """
        Update the Entity's annotation, can add new annotation
        if create=True
        """
        if isinstance(annotation, str):
            annotation_str = annotation

            try:
                annotation = Annotation.get((Annotation.name == annotation) & (
                    Annotation.component == self.component))
            except Annotation.DoesNotExist:
                logger.warning(f"Annotation {annotation_str} not available"
                               " for Component: {self.component.name}")
                if not create:
                    logger.error("Failed to update annotation!")
                    return
                else:
                    logger.info(f"Creating annotation: {annotation_str}")
                    annotation = self.component.add_annotation(annotation)

        elif isinstance(annotation, Annotation):
            if annotation.component != self.component:
                logger.error(
                    "Invalid Annotation given for {self.component.name}")
                raise ValueError

        self.annotation = annotation
        return

    def update_rating(self, rating: Union[str, Rating]):
        """
        Update the Entity's Rating
        """

        if isinstance(rating, str):
            rating_str = rating
            try:
                rating = Rating.get(Rating.name == rating)
            except Rating.DoesNotExist:
                logger.error(f"Invalid rating {rating_str}")
                return

        logger.info("Setting rating for {self.name} to {rating.name}")
        self.rating = rating

    def update_comment(self, comment: str):
        """
        Update the Entity's comment
        """
        self.comment = comment.strip('\n').strip(' ')

    def set_images(self, images: List[Path]):
        """
        Set images associated with Entity to `images`
        """

        with self.db.atomic():
            [image.delete_instance() for image in self.images]

        with self.db.atomic():
            [self.add_image(image) for image in images]

        self.save()

    def remove_qc(self):
        """
        Remove QC ratings on Entity
        """
        with self.db.atomic():
            self.annotation = None
            self.rating = None


class Image(BaseModel):
    '''
    Images used for an Entity to assess quality
    '''
    path = TextField(unique=True)
    entity = ForeignKeyField(Entity, backref='images')

    class Meta:
        database = database_proxy

        # Unique constraint on path-entity tuples
        indexes = ((("path", "entity"), True), )


DB_TABLES = [
    Component, Annotation, Rating, TableColumn, TableRow, Entity, Image
]
DB_TABLE_NAMES = [
    'component', 'annotation', 'rating', 'tablecolumn', 'tablerow', 'entity',
    'image'
]
