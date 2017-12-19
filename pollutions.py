import json
import access
import requests
import requests_cache
import logging
import csv
from collections import OrderedDict
from transliterate import translit, get_available_language_codes
from datetime import datetime
import re


def get_egfdm_authorization_session(url, data):
    session = requests.Session()
    response = session.post(access.url, data=access.data, verify=False)
    if response.status_code == 200:
        print(response)
    return session


def save_measurements_csv_file(session, file_name):
    headers = {'User-agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip'}
    session.get(access.today_h2s_url, headers=headers, verify=False)
    response = session.get(access.csv_url, headers=headers, verify=False)
    with open(file_name, mode='w', encoding='utf8') as code:
        code.write(response.text)



def get_stations_names_dict_from_csv(measurements_csv_file):
    with open(measurements_csv_file, 'r', encoding='utf-8') as f:
        reader_fields = csv.reader(f)
        for num, row in enumerate(reader_fields):
            if num == 0:
                fields_ru_list = row[0].split('\t')[1:]
                fields = [translit(mark, reversed=True) for mark in fields_ru_list]
                clear_fields = [re.sub("[\'\-\(\)]", '', st).strip().replace(' ', '_') for st in fields]
            else:
                break
        return OrderedDict(zip(clear_fields, fields_ru_list))


def get_stench_today(measurements_csv_file, stations_names_list):
    askza_value_list = OrderedDict()
    askza_alarm_value_list = OrderedDict()
    stations_names_list.insert(0, 'date')

    with open(measurements_csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, stations_names_list, delimiter='	')
        for num, row in enumerate(reader):
            if num not in (0, 1) and row['date'] != '' and row['Shabolovka'] != '':
                date = row['date']
                stench_datetime = datetime.strptime(date, "%d/%m/%Y %H:%M")
                del row['date']
                stench = {key: value for key, value in row.items() if value not in ('', None) and float(value) > 0.008}
                if stench:
                    askza_alarm_value_list[stench_datetime] = stench
                askza_value_list[date] = row
    return askza_alarm_value_list


def get_stenchs_str_list(stenchs_dict, stations_names_dict):
    stenchs_str_list = []
    for date, stench in sorted(stenchs_dict.items()):
        station_name = list(stench.keys())[0]
        measurment = list(stench.values())[0]
        stenchs_str_list.append('{} - {} : {}'.format(date.strftime('%d.%m.%Y %H:%M'),
                                                      stations_names_dict[station_name], measurment))
    return stenchs_str_list


def get_page(url):
    headers = {'User-agent': 'Mozilla/5.0', 'Accept-Encoding': 'gzip'}
    try:
        response = requests.get(url, headers=headers)
        logging.info('The page: {} get from {}'.format(url))
        return response
    except (ConnectionError, requests.exceptions.ConnectionError) as exc:
        logging.error(exc)
        return None


if __name__ == '__main__':

    session = get_egfdm_authorization_session(access.url, access.data)
    save_measurements_csv_file(session, 'egfdm1.csv')
    stations_names = get_stations_names_dict_from_csv('egfdm1.csv')
    stenchs = get_stench_today('egfdm1.csv', list(stations_names.keys()))
    print(('\n').join(get_stenchs_str_list(stenchs, stations_names)))