from peewee import (Model, ForeignKeyField, TextField, CharField, BooleanField,
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
    status = TextField(null=True)
    rating = ForeignKeyField(Annotation, null=False, backref='+')

    class Meta:
        database = database_proxy
        indexes = ((("name", ), True), )

    @property
    def entry(self):
        if self.rating:
            rating = self.rating.name
        else:
            rating = ""
        return (rating, self.status, self.comment or "")


class Image(BaseModel):
    '''
    Images used for an Entity to assess quality
    '''
    path = TextField(unique=True)
    entity = ForeignKeyField(Entity, backref='images')
