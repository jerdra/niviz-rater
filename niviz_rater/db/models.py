"""
Niviz Data Models
"""

from __future__ import annotations
from pathlib import Path
from typing import Union
import logging
from peewee import (Model, ForeignKeyField, TextField, CharField, BooleanField,
                    DatabaseProxy, IntegrityError)

logger = logging.getLogger(__name__)

database_proxy = DatabaseProxy()


class BaseModel(Model):

    class Meta:
        database = database_proxy


class Component(BaseModel):
    '''
    Component component ID
    '''

    name = CharField(unique=True)

    def add_annotation(self, annotation_name: str) -> Annotation:
        """
        Add an annotation to a component
        """

        annotation = Annotation.create(name=annotation_name, component=self)
        try:
            annotation.save()
        except IntegrityError:
            logger.error(f"Annotation {annotation_name} already exists for "
                         f"component {self.name}!")
            logger.error("Skipping creation...")
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
    is_default = BooleanField(default=False)

    class Meta:
        database = database_proxy

        # Unique constraint on name-component tuples
        indexes = ((("name", "component"), True), )


class Rating(BaseModel):
    '''
    Pass/Fail/Uncertain/None ratings
    '''
    name = CharField(unique=True)
    is_default = BooleanField(default=False)


class TableColumn(BaseModel):
    name = CharField(primary_key=True)


class TableRow(BaseModel):
    name = CharField(primary_key=True)


class Entity(Model):
    '''
    Single entity to QC
    '''
    name = CharField()
    columnname = ForeignKeyField(TableColumn, null=False, backref='entities')
    rowname = ForeignKeyField(TableRow, null=False, backref='entities')
    component = ForeignKeyField(Component, null=False, backref='+')
    comment = TextField(default="")
    rating = ForeignKeyField(Rating, null=False, backref='+')
    annotation = ForeignKeyField(Annotation, null=False, backref='+')

    class Meta:
        database = database_proxy
        indexes = ((("name", ), True), )

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

        return (annotation, rating, self.comment.replace("\n", "\\n") or "")

    def add_image(self, image_path: Path) -> Image:
        """
        Add image to Entity
        """
        image = Image(path=image_path, entity=self)
        try:
            image.save()
        except IntegrityError:
            logger.error(f"Image { image_path } is already being used for"
                         f" the Entity { self.name }")
            intended_image = Image.get((Image.path == image_path)
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
            annotation = Annotation.get((Annotation.name == annotation) & (
                Annotation.component == self.component))
            if not create:
                logger.error(f"Annotation {annotation_str} not available"
                             " for Component: {self.component.name}")
                logger.error("Failed to update annotation!")
                return
            else:
                annotation = self.component.add_annotation(annotation)

        self.annotation = annotation
        return

    def update_rating(self, rating: Union[str, Rating]):
        """
        Update the Entity's Rating
        """
        raise NotImplementedError

    def update_comment(self, comment: str):
        """
        Update the Entity's comment
        """
        raise NotImplementedError


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
