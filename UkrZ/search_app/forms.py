# -*- coding: utf-8 -*-
import requests

from django import forms
from django.conf import settings

from.models import SearchingInfo


def get_station(name):
    stations = requests.get(
        url=settings.UZ_HOST,
        params={'term': name},
    ).json()
    for station in stations:
        if station.get('title') == name:
            return station
    raise Exception('Available stations: {1}'.format(
        name,
        ', '.join(['"' + station.get('title') + '"' for station in stations])
    ))


class StationForm(forms.Form):
    station_from = forms.CharField(max_length=50, label='Станция отправлния')
    station_till = forms.CharField(max_length=50, label='Станция назначения')
    date_dep = forms.CharField(label='Дата')
    coach_type = forms.CharField(max_length=1, label='Тип места')

    def clean_station_from(self):
        name = self.cleaned_data.get('station_from')
        try:
            get_station(name)
        except Exception as inst:
            raise forms.ValidationError(inst.args[0])


class SearchForm(forms.ModelForm):

    class Meta:
        model = SearchingInfo
        fields = ['station_from', 'station_till', 'date_dep', 'coach_type']
