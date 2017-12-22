# coding: utf-8
import time
import datetime
import math

from django.utils import timezone
from django.core.mail import send_mail

from UkrZ.celery import app
from .models import SearchingInfo
from .uz import Direction


def mail_to(text, address):
    # send_mail(
    #     subject='Success',
    #     message=text,
    #     from_email='from@example.com',
    #     recipient_list=[address, ]
    # )
    print('I sent email({}) to address {}. Work is done.'.format(
        text,
        address
    ))


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


@app.task
def looking_for_coaches(search_id):
    messages = str()
    search = SearchingInfo.objects.get(id=search_id)
    message = 'Поиск {} не актуальный.'.format(search)
    direction = Direction(
        city_from=search.station_from,
        city_till=search.station_till,
        date_dep=search.date_dep,
        coach_type=search.coach_type
    )
    date_dep = get_date_from_string(search.date_dep)
    if date_dep < timezone.localdate():
        message = 'Дата отправления для направления "{} - {}" прошла. Поиск был остановлен.'.format(
            direction.station_from,
            direction.station_till
        )
        mail_to(
            text=message,
            address=search.author.email
        )
        search.is_actual = False
        search.save()
    is_actual = search.is_actual
    while is_actual:
        coaches = direction.get_good_coaches()
        if coaches and not isinstance(coaches, str):
            for train in coaches:
                best_carriage = [0, [], math.inf]
                for carriage in train['carriages']:
                    if len(carriage['coaches']) >= search.amount_of_coaches:
                        best_coaches = get_best_of_the_best(carriage['coaches'], search.amount_of_coaches)
                        if best_coaches[-1] < best_carriage[-1]:
                            best_carriage = [carriage['number'], ]
                            best_carriage.extend(best_coaches)
                        search.is_actual = is_actual = False
                        search.save()
                message = 'Поезд {}. Вагон №{}. Места: {}. '.format(
                    train['train'],
                    best_carriage[0],
                    ', '.join(best_carriage[1])
                )
                messages += message
                mail_to(
                    text='Дата отправления {}. '.format(search.date_dep) + message,
                    address=search.author.email
                )
            search.result = messages
            search.save()
        else:
            time.sleep(10)
    return messages or message
