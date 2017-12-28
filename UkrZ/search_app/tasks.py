# coding: utf-8
import time
import math

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from UkrZ.celery import app
from .models import SearchingInfo, SuccessResult, FailResult
from search_app import utils


@app.task
def mail_to(subject: str, text: str, address: list, html_message: str=None) -> str:
    send_mail(
        subject=subject,
        message=text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=address,
        html_message=html_message
    )
    return 'I sent email({}) to address {}.'.format(
        text,
        address
    )


@app.task
def looking_for_coaches(search_id: int):
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
                    search.station_from,
                    search.station_till
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
                        SuccessResult.objects.create(
                            train=train['train'],
                            date_from=train.get('date_from'),
                            date_till=train.get('date_till'),
                            carriage=best_carriage[0],
                            coaches=', '.join(best_carriage[1]),
                            searching_info=search
                        )
                        search.is_actual = False
                        search.save()
                        message = 'Success'
            else:
                time.sleep(10)
        except Exception as e:
            search.is_actual = False
            search.save()
            raise e
    if search.success_results.all().exists():
        context = {
            'station_from': search.station_from,
            'station_till': search.station_till,
            'date_dep': search.date_dep,
            'results': search.success_results.all(),
        }
        mail_to.delay(
            subject='Билеты успешно найдены.',
            text=render_to_string('success.txt', context=context),
            address=[search.author.email, ],
            html_message=render_to_string('success.html', context=context)
        )
    return message
