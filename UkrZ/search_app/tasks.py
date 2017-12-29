# coding: utf-8
import time

from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from UkrZ.celery import app
from .models import SearchingInfo, SuccessResult, FailResult, Carriage
from search_app import utils
from .uz import Direction, TrainException


@app.task
def mail_to(subject: str, text: str, address: list, html_message: str=None) -> str:
    send_mail(
        subject=subject,
        message=text,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=address,
        html_message=html_message
    )
    return 'I sent email to address {}.'.format(address)


@app.task
def looking_for_coaches(search_id: int):
    search = SearchingInfo.objects.get(id=search_id)
    try:
        message = 'Поиск {} не актуальный.'.format(search)
        direction = Direction(
            city_from=search.station_from,
            city_till=search.station_till,
            date_dep=search.date_dep,
            coach_type=search.coach_type
        )
        date_dep = utils.get_date_from_string(search.date_dep)
        amount_of_coaches = search.amount_of_coaches
        get_good = search.get_good or search.get_best
        get_best = search.get_best
        while search.is_actual:
            if date_dep < timezone.localdate():
                message = 'Дата отправления для направления "{} - {}" прошла. Поиск был остановлен.'.format(
                    direction.station_from.name,
                    direction.station_till.name
                )
                FailResult.objects.create(
                    searching_info=search,
                    fail_message=message
                )
                search.is_actual = False
                search.save()
                break

            try:
                direction.run()
            except TrainException:
                time.sleep(10)
                continue
            trains = direction.get_trains(amount=amount_of_coaches, get_good=get_good, get_best=get_best)
            if trains:
                for train in trains:
                    result = SuccessResult.objects.create(
                        train=train.number,
                        date_from=train.datetime_from,
                        date_till=train.datetime_till,
                        searching_info=search
                    )
                    for carriage in train.carriages:
                        Carriage.objects.create(
                            success_result=result,
                            number=carriage.number,
                            coaches=', '.join(carriage.coaches)
                        )
                search.is_actual = False
                search.save()
                message = 'Success'
    except Exception as e:
        search.is_actual = False
        search.save()
        raise e
    if search.success_results.all().exists():
        print(search.success_results.all().prefetch_related('carriages'))
        context = {
            'station_from': search.station_from,
            'station_till': search.station_till,
            'date_dep': search.date_dep,
            'results': search.success_results.all().prefetch_related('carriages'),
        }
        mail_to.delay(
            subject='Билеты успешно найдены.',
            text=render_to_string('success.txt', context=context),
            address=[search.author.email, ],
            html_message=render_to_string('success.html', context=context)
        )
    return message
