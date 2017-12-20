from peewee import *
from datetime import date
db = SqliteDatabase('files/stenches.db')


class BaseModel(Model):
    class Meta:
        database = db

#вонь
class Stench(BaseModel):
    citizen_request = ForeignKeyField(CitizenRequest, related_name='stenches', default=None)
    value = CharField()
    chemical = CharField()
    timestamp = DateTimeField()
    latitude = FloatField()
    longitude = FloatField()
    station = ForeignKeyField(Station, related_name='st_stenches', default=None)
    departure = ForeignKeyField(Station, related_name='dp_stenches', default=None)
    is_submit_telegram = BooleanField()

    class Meta:
        order_by = ('-timestamp',)

#станции
class Station(BaseModel):
    id = IntegerField()
    ru_name = CharField()
    en_name = CharField()
    address = TextField()
    email = CharField()
    is_relative = BooleanField()
    latitude = FloatField()
    longitude = FloatField()

    class Meta:
        order_by = ('-fio',)


#граждане
class Citizen(BaseModel):
    fio = CharField()
    address = TextField()
    email = CharField()
    is_relative = BooleanField()

    class Meta:
        order_by = ('-fio',)

#заявки граждан
class CitizenRequest(BaseModel):
    timestamp = DateTimeField()
    citizen = ForeignKeyField(Citizen, related_name='requests')
    content = TextField()
    incoming_number = CharField()
    call_id = CharField()
    request_type = CharField()
    condition = CharField()


    class Meta:
        order_by = ('-timestamp',)

#выезды
class Departure(BaseModel):
    timestamp = DateTimeField()
    url_act = CharField()
    citizenrequest = ForeignKeyField(Citizen, related_name='departures')


if __name__ == '__main__':

    db.connect()
    db.create_tables([Stench, Station, Citizen, CitizenRequest], safe=True)
