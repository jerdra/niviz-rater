from peewee import (Model, ForeignKeyField, TextField, CharField, BooleanField)
from niviz_rater import db


class BaseModel(Model):
    class Meta:
        database = db


class Component(BaseModel):
    '''
    Component component ID
    '''


class Rating(BaseModel):
    '''
    Rating ID --> named rating mapping
    '''
    name = CharField()
    component = ForeignKeyField(Component, null=False, backref='+')


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
    failed = BooleanField(null=True)
    rating = ForeignKeyField(Rating, null=True, backref='+')

    class Meta:
        database = db
        indexes = ((("name", ), True), )

    @property
    def has_failed(self):
        if self.failed is True:
            return "Fail"
        elif self.failed is False:
            return "Pass"
        else:
            return ""

    @property
    def entry(self):
        if self.rating:
            rating = self.rating.name
        else:
            rating = ""
        return (
            rating,
            self.has_failed,
            self.comment or ""
        )


class Image(BaseModel):
    '''
    Images used for an Entity to assess quality
    '''
    path = TextField(unique=True)
    entity = ForeignKeyField(Entity, backref='images')
