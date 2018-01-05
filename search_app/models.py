# coding: utf-8
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .utils import get_date_from_string


class SearchingInfo(models.Model):
    author = models.ForeignKey(get_user_model(), related_name='SearchRequests', on_delete=models.CASCADE)
    station_from = models.CharField('Станция отправления', max_length=50)
    station_till = models.CharField('Станция назначения', max_length=50)
    date_dep = models.CharField('Дата отправления', max_length=10)
    date_dep_in_datetime_format = models.DateField(null=True)
    COACHES_TYPES = (
        ('П', 'Плацкарт'),
        ('К', 'Купе'),
        ('Л', 'Люкс')
    )
    coach_type = models.CharField('Тип места', max_length=1, choices=COACHES_TYPES)
    amount_of_coaches = models.PositiveSmallIntegerField('Количество мест')
    create_date = models.DateField('Дата создания запроса', auto_now_add=True)
    is_actual = models.BooleanField('Актуальность', default=True)
    get_good = models.BooleanField('Искать только хорошие', default=False)
    get_best = models.BooleanField('Искать только лучшие', default=False)

    class Meta:
        ordering = ['date_dep_in_datetime_format']

    def __str__(self):
        return '{} >> {} {}'.format(
            self.station_from,
            self.station_till,
            self.date_dep
        )


class SuccessResult(models.Model):
    searching_info = models.ForeignKey(SearchingInfo, on_delete=models.CASCADE, related_name='success_results')
    train = models.CharField(max_length=128)
    date_from = models.DateTimeField()
    date_till = models.DateTimeField()
    create_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['-create_date', ]

    def __str__(self):
        return self.train


class Carriage(models.Model):
    success_result = models.ForeignKey(SuccessResult, on_delete=models.CASCADE, related_name='carriages')
    number = models.CharField(max_length=8)
    coaches = models.TextField()

    def __str__(self):
        return self.number


class FailResult(models.Model):
    searching_info = models.OneToOneField(SearchingInfo, on_delete=models.CASCADE, related_name='fail_result')
    fail_message = models.TextField()
    create_date = models.DateField(auto_now_add=True)


@receiver(post_save, sender=SearchingInfo)
def add_date_dep_in_datetime_format(sender, **kwargs):
    instance = kwargs.get('instance')
    if not instance.date_dep_in_datetime_format:
        instance.date_dep_in_datetime_format = get_date_from_string(instance.date_dep)
        instance.save()
