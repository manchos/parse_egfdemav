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


def en_station_translit(ru_name):
    en_name = translit(ru_name, reversed=True)
    clear_en_name = re.sub("[\"\'\(\).]", '', en_name).strip().replace(' ', '_')
    return clear_en_name


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
                clear_fields = [re.sub("[\'\-\(\).]", '', st).strip().replace(' ', '_') for st in fields]
            else:
                break
        return OrderedDict(zip(clear_fields, fields_ru_list))


def get_stench_today(measurements_csv_file, stations_names_list):
    askza_alarm_value_list = OrderedDict()
    stations_names_list.insert(0, 'date')

    with open(measurements_csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, stations_names_list, delimiter='	')
        stenches_numb = 0
        for num, row in enumerate(reader):
            if num not in (0, 1) and row['date'] != '' and row['Shabolovka'] != '':
                date = row['date']
                stench_datetime = datetime.strptime(date, "%d/%m/%Y %H:%M")
                del row['date']
                stench = {key: round(float(value)/0.008, 2) for key, value in row.items() if value not in ('', None)
                          and float(value) > 0.008}
                if stench:
                    stenches_numb = stenches_numb + len(stench)
                    try:
                        askza_alarm_value_list[stench_datetime].update(stench)
                    except KeyError:
                        askza_alarm_value_list.setdefault(stench_datetime)
                        askza_alarm_value_list[stench_datetime] = stench
    return stenches_numb, askza_alarm_value_list


def get_stenchs_str_list(stenchs_dict, stenches_numb, stations_names_dict):
    today = datetime.today()
    stenchs_str_list = ['']
    stenchs_str_list.append(today.strftime('%d.%m.%Y'))
    # print(stenchs_dict)
    for (date, stench_dict) in sorted(stenchs_dict.items()):
        # print('list_stench {}'.format(stench_dict))
        for station_name, measurment in stench_dict.items():
            stenchs_str_list.append('{} - {}: {}'.format(date.strftime('%H:%M'),
                                                      stations_names_dict[station_name].strip(), measurment))
    stenchs_str_list.append('\nВсего за {} - {} превышений'.format(today.strftime('%d.%m.%Y'), stenches_numb))
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
    stenches_numb, stenchs = get_stench_today('egfdm1.csv', list(stations_names.keys()))
    print(('\n').join(get_stenchs_str_list(stenchs, stenches_numb, stations_names)))