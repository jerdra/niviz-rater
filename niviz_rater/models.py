"""
Niviz Data Models
"""

from __future__ import annotations
import logging
from peewee import (Model, ForeignKeyField, TextField, CharField,
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

        annotation = Annotation.create(name=annotation_name,
                                       component=self.get_id())
        try:
            annotation.save()
        except IntegrityError:
            logger.error(f"Annotation {annotation_name} already exists for "
                         f"component {self.name}!")
            logger.error("Skipping creation...")
            intended_annot = Annotation.get(
                Annotation.component == self.get_id())
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


class Image(BaseModel):
    '''
    Images used for an Entity to assess quality
    '''
    path = TextField(unique=True)
    entity = ForeignKeyField(Entity, backref='images')
