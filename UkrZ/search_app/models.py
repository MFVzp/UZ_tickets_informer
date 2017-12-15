# coding: utf-8
from django.db import models


class SearchingInfo(models.Model):
    station_from = models.CharField('Станция отправления', max_length=50)
    station_till = models.CharField('Станция назначения', max_length=50)
    date_dep = models.DateField('Дата отправления', )
    COACHES_TYPES = (
        ('П', 'Плацкарт'),
        ('К', 'Купе'),
        ('Л', 'Люкс')
    )
    coach_type = models.CharField('Тип места', max_length=1, choices=COACHES_TYPES)
    create_date = models.DateField('Дата создания запроса', auto_now_add=True, auto_now=False)
    is_actual = models.BooleanField('Актуальность', default=True)
