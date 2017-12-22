from datetime import datetime
from peewee import *
from datetime import date
db = SqliteDatabase('files/stenches.db')


class BaseModel(Model):
    class Meta:
        database = db


#округ Москвы
class MoscowDistrict(BaseModel):
    long_name = CharField()
    short_name = CharField()
    population = IntegerField(null=True)
    area = IntegerField(null=True)
    polygon = TextField(null=True)



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
    district = CharField()

    class Meta:
        order_by = ('-timestamp',)


#станции
class Station(BaseModel):
    id_egfdm = IntegerField(primary_key=True, unique=True)
    ru_name = CharField()
    en_name = CharField()
    address = TextField(default='')
    short_address = TextField(default='')
    latitude = FloatField(default=0.0)
    longitude = FloatField(default=0.0)
    district = CharField(default='')

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

    # db.create_tables([MoscowDistrict, MoscowDistrict, Stench, Station, Citizen, CitizenRequest, Departure], safe=True)

    # station1 = Station.create(id_egfdm=18, ru_name='dddd', address='ddddd', en_name='Kozukhova')

    # # station1.save()
    # stench1 = Stench.create(value='1.45', chemical='h2s', timestamp=datetime.today(), station=Station.get(id_egfdm=18))

    stenches = Stench.get(is_submit_telegram=False)
    print(stenches.value, stenches.is_submit_telegram)
    # for stench in stenches:
    #     print(stench)
    # stenches.is_submit_telegram = True
    # print(stench1.is_submit_telegram)


    # stench1.is_submit_telegram = True

    station = Station.get(id_egfdm=18)
    # stenches1 = stenches
    # station1 = stenches1
    # for st in station:
    #     print(st)
    print(station.id_egfdm, station.ru_name)





    # print(stench1.is_submit_telegram)
    # stenches.save()