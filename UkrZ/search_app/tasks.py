# coding: utf-8
import time
import math

from django.utils import timezone
from django.core.mail import send_mail

from UkrZ.celery import app
from .models import SearchingInfo, SuccessResult, FailResult
from search_app import utils


@app.task
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


@app.task
def looking_for_coaches(search_id):
    messages = str()
    search = SearchingInfo.objects.get(id=search_id)
    message = 'Поиск {} не актуальный.'.format(search)
    direction = utils.Direction(
        city_from=search.station_from,
        city_till=search.station_till,
        date_dep=search.date_dep,
        coach_type=search.coach_type
    )
    date_dep = utils.get_date_from_string(search.date_dep)
    while search.is_actual:
        try:
            if date_dep < timezone.localdate():
                message = 'Дата отправления для направления "{} - {}" прошла. Поиск был остановлен.'.format(
                    direction.station_from['title'],
                    direction.station_till['title']
                )
                mail_to.delay(
                    text=message,
                    address=search.author.email
                )
                FailResult.objects.create(
                    searching_info=search,
                    fail_message=message
                )
                search.is_actual = False
                search.save()
                break
            coaches = direction.get_good_coaches()
            if coaches and not isinstance(coaches, str):
                for train in coaches:
                    best_carriage = [0, [], math.inf]
                    for carriage in train['carriages']:
                        if len(carriage['coaches']) >= search.amount_of_coaches:
                            best_coaches = utils.get_best_of_the_best(carriage['coaches'], search.amount_of_coaches)
                            if best_coaches[-1] < best_carriage[-1]:
                                best_carriage = [carriage['number'], ]
                                best_carriage.extend(best_coaches)
                    if best_carriage[0]:
                        res = SuccessResult.objects.create(
                            train=train['train'],
                            date_from=train.get('date_from'),
                            date_till=train.get('date_till'),
                            carriage=best_carriage[0],
                            coaches=', '.join(best_carriage[1]),
                            searching_info=search
                        )
                        search.is_actual = False
                        search.save()
                        message = 'Поезд {}. Вагон №{}. Места: {}. '.format(
                            res.train,
                            res.carriage,
                            res.coaches
                        )
                        messages += message
                        mail_to.delay(
                            text='Дата отправления {}. '.format(search.date_dep) + message,
                            address=search.author.email
                        )
            else:
                time.sleep(10)
        except Exception as e:
            search.is_actual = False
            search.save()
            raise e
    return messages or message
