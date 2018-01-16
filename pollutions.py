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
from  stenches_work import get_stenches_dict_from_file
from service import get_page, save_file
from robobrowser import RoboBrowser
from urllib.parse import urlencode


from datetime import datetime
import re


def get_egfdm_authorization_session(url, data, requests_cache):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br'}
    session = requests_cache.CachedSession()
    session.verify = False
    session.headers = headers
    response = session.post(url, data=data, headers=headers, verify=False)


    print(response.text)
    print(response.from_cache)

    if response.status_code == 200:
        print(response)
    return session


def get_egfdm_authorization_rb_session(url, data, requests_cache):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br'}
    session = requests_cache.CachedSession()
    browser = RoboBrowser()
    browser.session.headers = headers
    browser.session.verify = False
    # encoded_args = urlencode(data)
    browser.open(url)
    form = browser.get_form(action='/act/_login')
    form['logname'].value = data['logname']
    form['password'].value = data['password']
    form['entry_point'].value = data['entry_point']
    form['ctlid2752307'].value = data['ctlid2752307']
    form['login_url'].value = data['login_url']
    # form['lang']
    # url = '{url}/act/_login?login_url={login_url}&entry_point{entry_point}&'.format(url=url, **access.data )
    browser.submit_form(form)



    # response = session.post(url, data=data, headers=headers, verify=False)

    print(browser.response.text)
    print(browser.response.from_cache)

    if browser.response.status_code == 200:
        print(browser.response)
    return browser.session



def get_measurements_url(chemical_id=4, from_date=datetime.today(), to_date=datetime.today(),
                         url=access.measurments_url):
    return url.format(date_from=from_date.strftime('%d/%m/%Y'), hour_from=from_date.hour, min_from=from_date.minute,
                      date_to=to_date.strftime('%d/%m/%Y'), hour_to=to_date.hour, min_to=to_date.minute,
                      chemical_id=chemical_id)


def get_csv_url(content, url_template=access.csv_url):
    soup = BeautifulSoup(content, 'xml')
    page_id = soup.find('aui:screen-serial')['value']
    print('CSV URL: {}'.format(url_template))
    return url_template.format(page_id=page_id)


def get_measurements_csv_file(session, measurements_url=get_measurements_url()):
    with session.cache_disabled():
        measurments_page = get_page(measurements_url, session)
        print('{} from cache: {}'.format(measurements_url, measurments_page.from_cache))
        return get_page(get_csv_url(measurments_page.text), session)


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


def get_validate_date_from(str_date=0, str_hour=0, str_min=0):
    if not str_date:
        str_date = datetime.today().strftime('%d/%m/%Y')
    return validate_date(str_date, str_hour, str_min)


def get_validate_date_to(str_date=0, str_hour=23, str_min=59):
    if not str_date:
        str_date = datetime.today().strftime('%d/%m/%Y')
    return validate_date(str_date, str_hour, str_min)


def get_stenches_from_url(date_from_str, date_to_str, chemical_str,  chemicals_dict, stenches_dict):
    date_from = get_validate_date_from(date_from_str)
    date_to = get_validate_date_to(date_to_str)
    chemical_id = stations.get_chemical_id_from_db(chemical)
    if chemical_id:
        print(chemical_id.mem_id)


if __name__ == '__main__':

    if not os.path.exists('_cache'):
        os.mkdir('_cache')
    requests_cache.install_cache('_cache/page_cache', backend='sqlite',
                                 expire_after=86400)

    # s = requests_cache.CachedSession()

    # session = get_egfdm_authorization_rb_session(access.url, access.data, requests_cache)
    session = get_egfdm_authorization_session(access.url, access.data, requests_cache)


    stations_page = stations.get_stations_page(session, access.stations_url)
    #
    # stations_dict = stations.get_stations_dict_from_html(stations_page)
    # print(stations_dict)
    # # stations.stations_greate(stations_dict)
    chemicals_dict = stations.get_chemicals_dict_from_html(stations_page)



    # # stations.db_chemicals_greate(chemicals_dict)
    # print(chemicals_dict)
    #
    #
    #
    date_from = get_validate_date_from('29/12/2017')
    date_to = get_validate_date_to('29/12/2017')
    chemical = 'h2s'
    chemical_id = stations.get_chemical_id_from_db(chemical)
    if chemical_id:
        print(chemical_id.mem_id)

    print(date_from, date_to, chemical in chemicals_dict)


    #
    if date_from and date_to and chemical in chemicals_dict:
        measurements_url = get_measurements_url(chemicals_dict[chemical], date_from, date_to)
        print(measurements_url)
        content = get_measurements_csv_file(session, measurements_url)
        save_file('egfdm1.csv', content)

        stations_names = stations.get_stations_names_dict_from_csv('egfdm1.csv')
        print(stations_names)
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