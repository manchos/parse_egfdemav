import json
import access
import requests
import requests_cache
import logging
import csv
from collections import OrderedDict

# print(r2.text)


# with open(r2.text, 'r', encoding = 'utf-8') as f:
    # fields = ['title', 'image', 'published', 'content', 'email', 'first_name', 'last_name']


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


def get_stench_today(measurements_csv_file):
    askza_value_list = OrderedDict()
    askza_alarm_value_list = {}
    with open(measurements_csv_file, 'r',encoding='utf-8') as f:
        fields = ['date', 'shabolovka', 'marino', 'lublino', 'veshnyaki', 'kozuhova', 'kopotnya', 'golovacheva',
                  'gurianova', 'kuznecova', 'zulebino', 'novokosiono', 'lobachevskogo', 'reutov', 'balashiha-r',
                  'balashiha-s']
        reader = csv.DictReader(f, fields, delimiter='	')

        for num, row in enumerate(reader):
            if num not in (0, 1) and row['date'] != '' and row['shabolovka'] != '':
                date = row['date']
                del row['date']
                stench = {key: value for key, value in row.items() if value not in ('', None) and float(value) > 0.008}
                if stench:
                    askza_alarm_value_list[date] = stench
                askza_value_list[date] = row
    return askza_alarm_value_list




    # print(askza_value_list)
    # print(askza_alarm_value_list)



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
    save_measurements_csv_file(session, 'egfdm.csv')
    print(get_stench_today('egfdm.csv'))