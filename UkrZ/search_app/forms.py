# -*- coding: utf-8 -*-
import re

from django import forms
from django.conf import settings
from django.utils import timezone
import requests

from .models import SearchingInfo
from search_app import secondary_functions


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


class SearchForm(forms.ModelForm):

    class Meta:
        model = SearchingInfo
        fields = ['station_from', 'station_till', 'date_dep', 'coach_type', 'amount_of_coaches']

    def clean_station_from(self):
        station_from = self.cleaned_data.get('station_from')
        try:
            get_station(station_from)
        except ValueError as inst:
            raise forms.ValidationError(inst.args[0])
        return station_from

    def clean_station_till(self):
        station_till = self.cleaned_data.get('station_till')
        try:
            get_station(station_till)
        except ValueError as inst:
            raise forms.ValidationError(inst.args[0])
        return station_till

    def clean_date_dep(self):
        date_dep = self.cleaned_data.get('date_dep')
        if not re.match(r'\d{2}.\d{2}.\d{4}', date_dep):
            raise forms.ValidationError('Вы ввели неправильную дату. Введите дату еще раз в формате "дд.мм.гггг"')
        try:
            date_dep_in_date_format = secondary_functions.get_date_from_string(date_dep)
        except ValueError as e:
            raise forms.ValidationError(e.args[0])
        if date_dep_in_date_format < timezone.localdate():
            raise forms.ValidationError('Дата {} уже прошла. Сегодня {}. Введите актуальную дату.'.format(
                date_dep_in_date_format,
                timezone.localdate()
            ))
        return date_dep
