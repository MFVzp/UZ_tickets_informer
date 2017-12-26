# coding: utf-8
import time
import math

from django.utils import timezone

from UkrZ.celery import app
from .models import SearchingInfo, Result
from .uz import Direction
from search_app import secondary_functions


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
    date_dep = secondary_functions.get_date_from_string(search.date_dep)
    if date_dep < timezone.localdate():
        message = 'Дата отправления для направления "{} - {}" прошла. Поиск был остановлен.'.format(
            direction.station_from['title'],
            direction.station_till['title']
        )
        secondary_functions.mail_to(
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
                print(train.get('date_from'))
                best_carriage = [0, [], math.inf]
                for carriage in train['carriages']:
                    if len(carriage['coaches']) >= search.amount_of_coaches:
                        best_coaches = secondary_functions.get_best_of_the_best(carriage['coaches'], search.amount_of_coaches)
                        if best_coaches[-1] < best_carriage[-1]:
                            best_carriage = [carriage['number'], ]
                            best_carriage.extend(best_coaches)
                        search.is_actual = is_actual = False
                        search.save()
                res = Result.objects.create(
                    train=train['train'],
                    date_from=train.get('date_from'),
                    date_till=train.get('date_till'),
                    carriage=best_carriage[0],
                    coaches=', '.join(best_carriage[1]),
                    searching_info=search
                )
                message = 'Поезд {}. Вагон №{}. Места: {}. '.format(
                    res.train,
                    res.carriage,
                    res.coaches
                )
                messages += message
                secondary_functions.mail_to(
                    text='Дата отправления {}. '.format(search.date_dep) + message,
                    address=search.author.email
                )
            search.result = messages
            search.save()
        else:
            time.sleep(10)
    return messages or message
