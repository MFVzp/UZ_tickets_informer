# coding: utf-8
import datetime

import requests
from django.conf import settings


def get_date_from_string(date_text):
    date = list(map(int, date_text.split('.')))
    return datetime.date(date[-1], date[-2], date[-3])


def get_station(name):
    stations = requests.get(
        url=settings.UZ_HOST + 'purchase/station/',
        params={'term': name},
    ).json()
    for station in stations:
        if station.get('title') == name:
            return station
    raise ValueError('Станции "{0}" не существует.\nПохожие станции: {1}'.format(
        name,
        (', '.join(['"' + station.get('title') + '"' for station in stations]) or 'нет похожих станций')
    ))
