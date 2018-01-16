from peewee import *
from mafudb import Stench
import logging
from collections import OrderedDict
import os
import csv
from transliterate import translit, get_available_language_codes
from datetime import datetime
import re




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



def insert_stench(Stench_table, value, chemical, datetime, station=None, citizen_request=None):
    # peewee.IntegrityError
    try:
        Stench_table.create(value=value, chemical=chemical, timestamp=datetime, station=station, citizen_request=citizen_request)
    except IntegrityError:
        print('sdfds')
        logging.info('The stench of {chemical} with value: {value} from Station: {station} in {datetime} already exists'.
                     format(chemical=chemical, value=value, station=station.ru_name, datetime=datetime))


if __name__ == '__main__':
    pass
