from bs4 import BeautifulSoup
import access
from service import get_page
import logging
import time
import peewee
from collections import OrderedDict
# from pollutions import get_egfdm_authorization_session, get_stations_names_dict_from_csv, get_page
from transliterate import translit
# import mafudb
from mafudb import Station, Chemical, db, en_station_translit, DatabaseError
import re
import os
import csv
# import geopy
from geopy.geocoders import Yandex
import html5lib
logging.basicConfig(level=logging.INFO)


def get_stations_names_dict_from_csv(measurements_csv_file):
    if not os.path.exists(measurements_csv_file):
        return None
    with open(measurements_csv_file, 'r', encoding='utf-8') as f:
        reader_fields = csv.reader(f)
        for num, row in enumerate(reader_fields):
            if num == 0:
                fields_ru_list = row[0].split('\t')[1:]
                fields = [translit(mark, reversed=True) for mark in fields_ru_list]
                clear_fields = [re.sub("[\'\-\(\).]", '', st).strip().replace(' ', '_') for st in fields]
            else:
                break
        return OrderedDict(zip(clear_fields, fields_ru_list))



def get_stations_dict_from_html(html):
    if html is not None:
        soup = BeautifulSoup(html.text, 'xml')
        stations_xmllist = soup.find(id='select___ASKZAStationStationID')
        return {st.get_text(): st.get('v')  for st in stations_xmllist.find_all('aui:o-s', string=True)
                         if st.get('v') != ''}


def get_chemicals_dict_from_html(html):
    if html is not None:
        soup = BeautifulSoup(html.text, 'xml')
        stations_xmllist = soup.find(id='select___ASKZAParameterParameterID')
        return {st.get_text().lower(): st.get('v')  for st in stations_xmllist.find_all('aui:o-s', string=True)
                         if st.get('v') != ''}


def get_stations_page(session, stations_url):
    return get_page(stations_url, session)


def get_moscow_district(longitude, latitude, session=None):
    district_url = 'https://geocode-maps.yandex.ru/1.x/?geocode={},{}&kind=district&results=5&format=json'\
        .format(longitude, latitude)
    response = get_page(district_url, session, verify=False)
    return response.json()['response']['GeoObjectCollection']['featureMember'][1]['GeoObject']['name']


def get_district_short_name(district_full_name): #'юго-восточный административный округ'
    district = district_full_name.strip()
    if '-' in district_full_name:
        re_ = re.findall('^([а-яА-Я]+)[ ]?[-]{1}[ ]?([а-яА-Я]+)', district)[0]
    else:
        re_ = re.findall('^([а-яА-Я]+)[ ]+', district)
    return ''.join([a[:1].upper() for a in re_]) + 'АО' #ЮВАО


def db_stations_greate(stations_ids_dict):
    if stations_ids_dict is not None:
        for ru_name, id in stations_ids_dict.items():
            # print('{}: {}'.format(ru_name.strip(), id))
            # print(en_station_translit(ru_name))
            try:
                Station.create(mem_id=id, ru_name=ru_name.strip(), en_name=en_station_translit(ru_name.strip()))
            except peewee.IntegrityError as ex:
                logging.info(ex)
                continue


def get_chemical_id_from_db(chemical_name):
    try:
        chemical = Chemical.get(Chemical.mem_name == chemical_name.strip())
    except Chemical.DoesNotExist as exc:
        logging.info(exc)
        return None
    return chemical

# #вещества
# class Chemical(BaseModel):
#     mem_id = IntegerField(primary_key=True, unique=True)
#     mem_name = CharField()
#     full_name = CharField()
#     formula = CharField()
#     description = TextField()
#     mem_pdk = FloatField()
#     pdk = FloatField

def db_chemicals_greate(chemicals_ids_dict):
    if chemicals_ids_dict is not None:
        for name, id in chemicals_ids_dict.items():
            # print('{}: {}'.format(ru_name.strip(), id))
            # print(en_station_translit(ru_name))
            try:
                Chemical.create(mem_id=id, mem_name=name.strip())
            except peewee.IntegrityError as ex:
                logging.info(ex)
                continue



# <button type="button" name="_fullscreen" class="pushButton" title="Показывать меньше строк" onclick="async_subst_get('/wnd/this/_setmediumpage/10,_layer=t1,_this=1374','divt1');"><img alt="Показывать меньше строк" src="/images/icons/vf/table_roll.png" width="16px" height="16px"></button>


def get_measurments_csv_url(soup):
    measurments_csv_url = soup.find(attrs={"name": "_fullscreen", "class": "pushButton"})['onclick']
    return measurments_csv_url


if __name__ == '__main__':
    # a = 'южный  административный округ'
    # print(get_district_short_name(a))


    db.connect()
    session = get_egfdm_authorization_session(access.url, access.data)
    stations_page = get_stations_page(session, access.stations_url)

    stations_ids_dict = get_stations_ids_dict(stations_page)



    chemicals_ids_dict = get_chemicals_ids_dict(stations_page)



    print(chemicals_ids_dict['h2s'])

    # db_stations_greate(stations_ids_dict)

    # db_chemicals_greate(chemicals_ids_dict)

            # time.sleep(5)

    # geolocator = Yandex()
    # location = geolocator.geocode("Маршала Полубоярова ул., 8")
    # print(location.raw['metaDataProperty']['GeocoderMetaData']['text'])
    # print(get_moscow_district(location.longitude, location.latitude))

# print(location.address)
# print((location.latitude, location.longitude))


            # stations.append({'id_egfdm': id,
            #                  'ru_name': ru_name,
            #                  'en_name': en_station_translit(ru_name),
            #                  'address': location.raw['metaDataProperty']['GeocoderMetaData']['text'],
            #                  'latitude': location.latitude,
            #                  'longitude': location.longitude,
            #                  'district': location.
            #                  }
            #                 )





# # станции
# class Station(BaseModel):
#     id_egfdm = IntegerField(primary_key=True, unique=True)
#     ru_name = CharField()
#     en_name = CharField()
#     address = TextField(default='')
#     latitude = FloatField(default=0.0)
#     longitude = FloatField(default=0.0)
#
#     class Meta:
#         order_by = ('-id_egfdm',)

