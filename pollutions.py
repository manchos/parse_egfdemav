import json
import access
import requests
import requests_cache
import logging
import csv
from collections import OrderedDict
from transliterate import translit, get_available_language_codes
import stations
import os
from bs4 import BeautifulSoup


from datetime import datetime
import re


def get_egfdm_authorization_session(url, data):
    session = requests_cache.CachedSession()
    response = session.post(access.url, data=access.data, verify=False)
    print(response.from_cache)
    if response.status_code == 200:
        print(response)
    return session


def get_measurements_url(chemical_id=4, from_date=datetime.today(), to_date=datetime.today(),
                         url=access.measurments_url):
    return url.format(date_from=from_date.strftime('%d/%m/%Y'), hour_from=from_date.hour, min_from=from_date.minute,
                      date_to=to_date.strftime('%d/%m/%Y'), hour_to=to_date.hour, min_to=to_date.minute,
                      chemical_id=chemical_id)


def get_csv_url(content, url_template=access.csv_url):
    soup = BeautifulSoup(content, 'xml')
    page_id = soup.find('aui:screen-serial')['value']
    return url_template.format(page_id=page_id)


def get_measurements_csv_file(session, measurements_url=get_measurements_url()):
    with session.cache_disabled():
        measurments_page = get_page(measurements_url, session)
        print('{} from cache: {}'.format(measurements_url, measurments_page.from_cache))
        return get_page(get_csv_url(measurments_page.text), session)



def save_file(file_name, content):
    with open(file_name, mode='w', encoding='utf8') as code:
        code.write(content.text)


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


def get_stenches_dict_from_file(measurements_csv_file, stations_names_list):
    stations_names_list.insert(0, 'date')
    askza_alarm_values_dict = OrderedDict()
    stenches_numb = 0
    pdk = 0.0
    if not os.path.exists(measurements_csv_file):
        return None
    with open(measurements_csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, stations_names_list, delimiter='	')
        for num, row in enumerate(reader):
            if num == 1:
                # row.items()[0]
                pdk = float(row.popitem()[1])
                print(pdk)
            if num == 2: # to avoid empty values row
                station_kontrol_empty_name = next(iter(row.keys()))
            if num not in (0, 1) and row['date'] != '' and row[station_kontrol_empty_name] != '':
                date = row['date']
                stench_datetime = datetime.strptime(date, "%d/%m/%Y %H:%M")
                del row['date']
                stench = {key: round(float(value)/0.008, 2) for key, value in row.items() if value not in ('', None)
                          and float(value) > pdk}
                if stench:
                    stenches_numb = stenches_numb + len(stench)
                    try:
                        askza_alarm_values_dict[stench_datetime].update(stench)
                    except KeyError:
                        askza_alarm_values_dict.setdefault(stench_datetime)
                        askza_alarm_values_dict[stench_datetime] = stench

        return stenches_numb, askza_alarm_values_dict


def get_stenchs_str_list(stenchs_dict, stenches_numb, stations_names_dict,
                         from_datetime=datetime.today(), to_datetime=datetime.today()):
    if (to_datetime - from_datetime).days > 0:
        title = '{} - {}'.format(from_datetime.strftime('%d.%m.%Y %H:%M'), to_datetime.strftime('%d.%m.%Y %H:%M'))
    else:
        title = '{}'.format(from_datetime.strftime('%d.%m.%Y '))
    stenchs_str_list = ['']
    stenchs_str_list.append(title)
    # print(stenchs_dict)
    for (date, stench_dict) in sorted(stenchs_dict.items()):
        # print('list_stench {}'.format(stench_dict))
        for station_name, measurment in stench_dict.items():
            stenchs_str_list.append('{} - {}: {}'.format(date.strftime('%H:%M'),
                                                      stations_names_dict[station_name].strip(), measurment))
    stenchs_str_list.append('\nВсего за {} - {} превышений'.format(title, stenches_numb))
    return stenchs_str_list


# def stenches_all


def get_page(url, session=None, verify=False):
    headers = {'User-agent': 'Mozilla/5.0', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip'}
    try:
        if session is not None:
            return session.get(url, headers=headers, verify=verify)
        else:
            return requests.get(url, headers=headers, verify=verify)
    except (ConnectionError, requests.exceptions.ConnectionError) as exc:
        logging.error(exc)
        return None


def validate_date(str_date, str_hour, str_min):
    [datetime_, hour, minut] = [0, 0, 0]
    date_match = re.search('^\d{1,2}/\d{1,2}/\d{4}', str_date)
    if date_match:
        try:
            datetime_ = datetime.strptime(date_match.group(), "%d/%m/%Y")
            if 0 <= int(str_hour) <= 23:
                hour = int(str_hour)
            if 0 <= int(str_min) <= 60:
                minut = int(str_min)
                datetime_ = datetime_.replace(hour=hour, minute=minut)
        except (ValueError, AttributeError) as er:
            logging.error(er)
            return None
        return datetime_

#=datetime.today().strftime('%d/%m/%Y')
def get_validate_date_from(str_date=0, str_hour=0, str_min=0):
    if not str_date:
        str_date = datetime.today().strftime('%d/%m/%Y')
    return validate_date(str_date, str_hour, str_min)


def get_validate_date_to(str_date=0, str_hour=23, str_min=59):
    if not str_date:
        str_date = datetime.today().strftime('%d/%m/%Y')
    return validate_date(str_date, str_hour, str_min)



if __name__ == '__main__':

    if not os.path.exists('_cache'):
        os.mkdir('_cache')
    requests_cache.install_cache('_cache/page_cache', backend='sqlite',
                                 expire_after=86400)

    # s = requests_cache.CachedSession()

    session = get_egfdm_authorization_session(access.url, access.data)

    chemicals_dict = stations.get_chemicals_ids_dict(session, access.stations_url)
    stations_dict = stations.get_stations_ids_dict(session, access.stations_url)
    stations.stations_greate(stations_dict)
    print(stations_dict)


    date_from = get_validate_date_from('29/12/2017')
    date_to = get_validate_date_to('29/12/2017')
    chemical = 'co'

    print(date_from, date_to, chemical in chemicals_dict)


    #
    if date_from and date_to and chemical in chemicals_dict:
        measurements_url = get_measurements_url(chemicals_dict[chemical], date_from, date_to)
        print(measurements_url)
        save_file('egfdm1.csv', get_measurements_csv_file(session, measurements_url))
        stations_names = get_stations_names_dict_from_csv('egfdm1.csv')
        # print(stations_names)
        # print(list(stations_names.keys()))
        stenches_numb, stenchs = get_stenches_dict_from_file('egfdm1.csv', list(stations_names.keys()))
        print(('\n').join(get_stenchs_str_list(stenchs, stenches_numb, stations_names, date_from, date_to)))
    else:
        logging.error("Неправильные значения дат")


    # (chemical_id = 4, from_date = datetime.today(), from_hour = '0', from_min = '0',
    #                       0                                                      to_date = datetime.today(), to_hour = '23', to_min = '59', url = access.measurments_url)
    # get_measurements_csv_file(session, measurements_url)



    # # #
    # stations_names = get_stations_names_dict_from_csv('egfdm1.csv')
    # # #
    # stenches_numb, stenchs = get_stenches_dict_from_file('egfdm1.csv', list(stations_names.keys()))
    #
    # for time, stench_value in stenchs.items():
    #     print(time, stench_value)
    #     # stations.insert_stench(value, chemical, datetime, station=None)
    #
    # print(date_to)
    # print(('\n').join(get_stenchs_str_list(stenchs, stenches_numb, stations_names, date_from, date_to)))


    # print(get_stenches_url())