from bs4 import BeautifulSoup
import requests
import access
import re
import logging
import time

from collections import OrderedDict
from pollutions import get_egfdm_authorization_session, get_stations_names_dict_from_csv, get_page
from transliterate import translit
from dbstenchs import Station, db
import re
# import geopy
from geopy.geocoders import Yandex
import html5lib
logging.basicConfig(level=logging.INFO)


def utf8_encode(txt, encoding):
    return bytes(txt, encoding).decode('utf-8')






def get_stations_ids_dict(session, stations_url):
    stations_page = get_page(stations_url, session)
    if stations_page is not None:
        soup = BeautifulSoup(stations_page.text, 'xml')
        stations_xmllist = soup.find(id='select___ASKZAStationStationID')
        return {st.get_text(): st.get('v')  for st in stations_xmllist.find_all('aui:o-s', string=True)
                         if st.get('v') != ''}


def get_chemicals_ids_dict(session, stations_url):
    stations_page = get_page(stations_url, session)
    if stations_page is not None:
        soup = BeautifulSoup(stations_page.text, 'xml')
        stations_xmllist = soup.find(id='select___ASKZAParameterParameterID')
        return {st.get_text().lower(): st.get('v')  for st in stations_xmllist.find_all('aui:o-s', string=True)
                         if st.get('v') != ''}


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


def stations_greate(session):
    stations_ids_dict = get_stations_ids_dict(session, access.stations_url)
    if stations_ids_dict is not None:
        for ru_name, id in stations_ids_dict.items():
            # print('{}: {}'.format(ru_name.strip(), id))
            # print(en_station_translit(ru_name))
            Station.create(id_egfdm=id, ru_name=ru_name.strip(), en_name=en_station_translit(ru_name.strip()))



if __name__ == '__main__':
    # a = 'южный  административный округ'
    # print(get_district_short_name(a))


    db.connect()
    session = get_egfdm_authorization_session(access.url, access.data)

    # stations_greate(session)

    chemicals_ids_dict = get_chemicals_ids_dict(session, access.stations_url)

    print(get_chemicals_ids_dict(session, access.stations_url)['h2s'])

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

