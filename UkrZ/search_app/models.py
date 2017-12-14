# coding: utf-8
from django.db import models


class SearchingInfo(models.Model):
    station_from = models.CharField(max_length=50)
    station_till = models.CharField(max_length=50)
    date_dep = models.CharField(max_length=50)
    COACHES_TYPES = (
        ('П', 'Плацкарт'),
        ('К', 'Купе'),
        ('Л', 'Люкс')
    )
    coach_type = models.CharField(max_length=1, choices=COACHES_TYPES)
    create_date = models.DateField(auto_now_add=True, auto_now=False)
    is_actual = models.BooleanField(default=True)
