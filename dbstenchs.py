from datetime import datetime
from peewee import *
from datetime import date
db = SqliteDatabase('files/stenches.db')


class BaseModel(Model):
    class Meta:
        database = db


#граждане
class Citizen(BaseModel):
    name = CharField()
    surname = CharField()
    address = TextField()
    email = CharField()
    is_relative = BooleanField()

    class Meta:
        order_by = ('-surname',)


#заявки граждан
class CitizenRequest(BaseModel):
    timestamp = DateTimeField()
    citizen = ForeignKeyField(Citizen, related_name='requests')
    content = TextField(default='')
    incoming_number = CharField()
    call_id = CharField()
    documents_url = CharField()
    request_type = CharField()
    condition = CharField()

    class Meta:
        order_by = ('-timestamp',)


#станции
class Station(BaseModel):
    id_egfdm = IntegerField(primary_key=True, unique=True)
    ru_name = CharField()
    en_name = CharField()
    address = TextField(default='')
    latitude = FloatField(default=0.0)
    longitude = FloatField(default=0.0)

    class Meta:
        order_by = ('-id_egfdm',)


#выезды
class Departure(BaseModel):
    timestamp = DateTimeField()
    url_act = CharField()
    citizenrequest = ForeignKeyField(Citizen, related_name='departures')


#вонь
class Stench(BaseModel):
    value = FloatField()
    chemical = CharField()
    timestamp = DateTimeField()
    latitude = FloatField(default=0.0)
    longitude = FloatField(default=0.0)
    is_submit_telegram = BooleanField(default=False)
    station = ForeignKeyField(Station, related_name='st_stenches', null=True)
    departure = ForeignKeyField(Departure, related_name='dp_stenches', null=True)
    citizen_request = ForeignKeyField(CitizenRequest, related_name='stenches', null=True)

    class Meta:
        order_by = ('-timestamp',)





if __name__ == '__main__':

    db.connect()
    # db.create_tables([Stench, Station, Citizen, CitizenRequest, Departure], safe=True)
    # station1 = Station(id_egfdm=18, ru_name='dddd', address='ddddd', en_name='Kozukhova')
    # # station1.save()
    # stench1 = Stench.create(value='1.45', chemical='h2s', timestamp=datetime.today(),
    #                         station=station1)





    # stench1.is_submit_telegram = True

    stenches = Stench.get(Stench.station == 18)
    print(stenches.station_id)
    print(stenches.is_submit_telegram)

    # stenches.is_submit_telegram = True



    # print(stench1.is_submit_telegram)
    # stenches.save()