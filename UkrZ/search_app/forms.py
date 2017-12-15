# -*- coding: utf-8 -*-
import re

from django import forms
from django.conf import settings
import requests

from .models import SearchingInfo


def get_station(name):
    stations = requests.get(
        url=settings.UZ_HOST + 'purchase/station/',
        params={'term': name},
    ).json()
    for station in stations:
        if station.get('title') == name:
            return station
    raise Exception('Станции "{0}" не существует.\nПохожие станции: {1}'.format(
        name,
        (', '.join(['"' + station.get('title') + '"' for station in stations]) or 'нет похожих станций')
    ))


class SearchForm(forms.ModelForm):

    class Meta:
        model = SearchingInfo
        fields = ['station_from', 'station_till', 'date_dep', 'coach_type']

    def clean(self):
        station_from = self.cleaned_data.get('station_from')
        station_till = self.cleaned_data.get('station_till')
        try:
            get_station(station_from)
            get_station(station_till)
        except Exception as inst:
            raise forms.ValidationError(inst.args[0])

        date_dep = self.cleaned_data.get('date_dep')
        if not re.match(r'\d{2}.\d{2}.\d{4}', date_dep):
            raise forms.ValidationError('Вы ввели неправильную дату. введи дату еще раз в формате "дд.мм.гггг"')

        return super(SearchForm, self).clean()
