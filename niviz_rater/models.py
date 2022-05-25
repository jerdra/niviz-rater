from peewee import (Model, ForeignKeyField, TextField, CharField,
                    DatabaseProxy)

database_proxy = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = database_proxy


class Component(BaseModel):
    '''
    Component component ID
    '''


class Annotation(BaseModel):
    '''
    Annotation ID --> named rating mapping
    '''
    name = CharField()
    component = ForeignKeyField(Component, null=False, backref='+')

class Rating(BaseModel):
    '''
    Pass/Fail/Uncertain/None ratings
    '''
    name = CharField()


class Rating(BaseModel):
    name = CharField()


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
        return (annotation, self.rating.name, self.comment or "")


class Image(BaseModel):
    '''
    Images used for an Entity to assess quality
    '''
    path = TextField(unique=True)
    entity = ForeignKeyField(Entity, backref='images')
