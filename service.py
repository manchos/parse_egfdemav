import logging
import requests
import re
from robobrowser import RoboBrowser


def save_file(file_name, content):
    with open(file_name, mode='w', encoding='utf8') as code:
        code.write(content.text)


def get_page(url, session=None, verify=False):
    headers = {'User-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:57.0) Gecko/20100101 Firefox/57.0', 'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3', 'Accept-Encoding': 'gzip, deflate, br'}
    try:
        if session is not None:
            # return browser
            return session.get(url, headers=headers, verify=verify)
        else:
            return requests.get(url, headers=headers, verify=verify)
    except (ConnectionError, requests.exceptions.ConnectionError) as exc:
        logging.error(exc)
        return None

def utf8_encode(txt, encoding):
    return bytes(txt, encoding).decode('utf-8')