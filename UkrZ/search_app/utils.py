# coding: utf-8
import datetime
import math

import requests
from django.conf import settings


def get_date_from_string(date_text):
    date = list(map(int, date_text.split('.')))
    return datetime.date(date[-1], date[-2], date[-3])


def sum_of_odds(numbers_list):
    res = 0
    for i in range(len(numbers_list[:-1])):
        res += numbers_list[i+1] - numbers_list[i]
    return res


def get_best_of_the_best(coaches_list, amount):
    the_best_combination = [[], math.inf]
    for i in range(len(coaches_list[:len(coaches_list) + 1 - amount])):
        combination = coaches_list[i:i+amount]
        difference_between_coaches = sum_of_odds(list(map(int, combination)))
        if difference_between_coaches < the_best_combination[1]:
            the_best_combination = [combination, difference_between_coaches]
    return the_best_combination


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
