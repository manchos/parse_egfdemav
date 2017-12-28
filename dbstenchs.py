from datetime import datetime
from peewee import *
# from peewee import
from datetime import date
db = SqliteDatabase('files/stenches.db')

from transliterate import translit, get_available_language_codes
import re

import logging
logging.basicConfig(level=logging.INFO)

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
        indexes = (
            # create a unique on from/to/date
            (('station', 'timestamp', 'value'), True),
            # create a non-unique on from/to
            # (('from_acct', 'to_acct'), False),
        )


def en_station_translit(ru_name):
    en_name = translit(ru_name, reversed=True)
    clear_en_name = re.sub("[\"\'\(\).]", '', en_name).strip().replace(' ', '_')
    return clear_en_name


def insert_station(id_egfdm, ru_name):
    # peewee.IntegrityError
    try:
        Station.create(id_egfdm=id_egfdm, ru_name=ru_name, en_name=en_station_translit(ru_name))
    except IntegrityError:
        logging.info('The Station with id: {} already exists'.format(id_egfdm))


def insert_stench(value, chemical, datetime, station=None):
    # peewee.IntegrityError
    try:
        Stench.create(value=value, chemical=chemical, timestamp=datetime, station=station)
    except IntegrityError:
        print('sdfds')
        logging.info('The stench with value: {} from Station: {} in {} already exists'.format(value, station.ru_name, datetime))






if __name__ == '__main__':

    db.connect()

    # db.create_tables([MoscowDistrict, MoscowDistrict, Stench, Station, Citizen, CitizenRequest, Departure], safe=True)
    db.create_tables([Stench], safe=True)

    # station1 = Station.create(id_egfdm=18, ru_name='dddd', address='ddddd', en_name='Kozukhova')
    insert_station(18, 'Станция 18')

    # # station1.save()
    # stench1 = Stench.create(value='1.45', chemical='h2s', timestamp=datetime.today(), station=Station.get(id_egfdm=18))

    d = datetime(2010, 7, 4, 12, 15, 58)

    insert_stench('1.45', 'h2s', d, Station.get(id_egfdm=18))

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