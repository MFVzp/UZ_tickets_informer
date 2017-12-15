# coding: utf-8
from django.db import models
from django.contrib.auth import get_user_model


class SearchingInfo(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='SearchRequests', on_delete=models.CASCADE)
    station_from = models.CharField('Станция отправления', max_length=50)
    station_till = models.CharField('Станция назначения', max_length=50)
    date_dep = models.CharField('Дата отправления', max_length=10)
    COACHES_TYPES = (
        ('П', 'Плацкарт'),
        ('К', 'Купе'),
        ('Л', 'Люкс')
    )
    coach_type = models.CharField('Тип места', max_length=1, choices=COACHES_TYPES)
    amount_of_coaches = models.PositiveSmallIntegerField('Количество мест')
    create_date = models.DateField('Дата создания запроса', auto_now_add=True, auto_now=False)
    is_actual = models.BooleanField('Актуальность', default=True)

    class Meta:
        ordering = ['is_actual', '-create_date']

    def __str__(self):
        return '{} >> {} {}'.format(
            self.station_from,
            self.station_till,
            self.date_dep
        )
