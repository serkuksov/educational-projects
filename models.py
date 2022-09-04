from peewee import SqliteDatabase, Model, AutoField, TextField, DateTimeField, DateField, PrimaryKeyField, CharField, \
    IntegerField

db = SqliteDatabase('avito.db')
db2 = SqliteDatabase('parser.db')

class BaseModel(Model):
    class Meta:
        database = db


class Garage(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    href = CharField()
    price = IntegerField()
    new_price = IntegerField(null=True)
    type = CharField()
    adres = CharField()
    creation_time = DateTimeField()
    new_creation_time = DateTimeField(null=True)
    description = CharField()
    date_change = DateField()
    date_deletion = DateField(null=True)

    class Meta:
        table_name = 'Garages'
        order_by = 'id'

class Coinmarketcap(BaseModel):
    name = CharField()
    platform = CharField()
    description = CharField()
    mintPrice = CharField()
    discord = CharField()
    twitter = CharField()
    website = CharField()
    dateTime = DateTimeField()
    preview = CharField()

