# coding: utf-8
import datetime
import time

import requests


class TrainException(Exception):
    """
    Raise it when request return error.
    """


class Station:

    def __init__(self, direction, name: str):
        stations = Direction.make_request(
            direction,
            resource='purchase/station/',
            params={'term': name},
        )
        for station in stations:
            if station.get('title') == name:
                self.name = name
                self.id = station.get('value')
                break
        else:
            raise ValueError('Вы ищете: "{0}". Доступные станции: {1}'.format(
                name,
                ', '.join(['"' + station.get('title') + '"' for station in stations])
            ))

    def __str__(self):
        return self.name


class Train:

    @classmethod
    def from_dict(cls, data):
        obj = super(Train, cls).__new__(cls)
        kwargs = {
            'number': data.get('num'),
            'travel_time': data.get('travel_time'),
            'date_dep_code': data['from']['date'],
            'end_station_from': data['from']['station'],
            'end_station_till': data['till']['station'],
            'datetime_from': datetime.datetime.strptime(data['from']['src_date'], "%Y-%m-%d %H:%M:%S"),
            'datetime_till': datetime.datetime.strptime(data['till']['src_date'], "%Y-%m-%d %H:%M:%S"),
            'places': [(place_type.get('id'), place_type.get('places')) for place_type in data.get('types')],
            'carriages': list()
        }
        obj.__init__(**kwargs)
        return obj

    def __init__(self, *args, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '\nПоезд №{} {} - {}\nВагоны:\n\t{}'.format(
            self.number,
            self.end_station_from,
            self.end_station_till,
            '\n\t'.join([carriage.__str__() for carriage in self.carriages])
        )


class Carriage:

    @classmethod
    def from_dict(cls, data):
        obj = super(Carriage, cls).__new__(cls)
        kwargs = {
            'number': data.get('num'),
            'coach_class': data.get('coach_class'),
            'coaches': list(),
        }
        obj.__init__(**kwargs)
        return obj

    def __init__(self, *args, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        return '№{}, места: {}'.format(
            self.number,
            ', '.join(self.coaches)
        )


class Direction:

    def __init__(self,
                 city_from,
                 city_till,
                 date_dep,
                 coach_type='П',
                 url='https://booking.uz.gov.ua/ru/'
                 ):
        self.url = url
        self.station_from = Station(self, city_from)
        self.station_till = Station(self, city_till)
        self.date_dep = date_dep
        self.coach_type = coach_type
        self.trains = list()

    def __str__(self):
        return 'Направление {} - {} | Дата: {} | Тип мест: {}\n\n{}'.format(
            self.station_from,
            self.station_till,
            self.date_dep,
            self.coach_type,
            '\n'.join([train.__str__() for train in self.trains])
        )

    def make_request(self, resource, data=None, params=None, method='GET', headers=None):
        url = self.url + resource
        response = requests.request(
            method=method,
            url=url,
            data=data,
            params=params,
            headers=headers
        ).json()
        time.sleep(0.1)
        if isinstance(response, dict) and response.get('error'):
            raise TrainException(
                '{}\nRequest args:\n\tmethod: {}\n\turl: {}\n\tdata: {}\n\tparams: {}\n\theaders: {}'.format(
                    response.get('value'),
                    method,
                    url,
                    data,
                    params,
                    headers
                )
            )
        return response

    def get_trains(self):
        trains = self.make_request(
            method='POST',
            resource='purchase/search/',
            data={
                'station_id_from': self.station_from.id,
                'station_id_till': self.station_till.id,
                'date_dep': self.date_dep,
            }
        )
        for train in trains.get('value'):
            if [coach_type for coach_type in train.get('types') if coach_type.get('id') == self.coach_type]:
                self.trains.append(Train.from_dict(data=train))
        if not self.trains:
            raise TrainException(
                'По заданному Вами направлению мест типа "{}" нет.'.format(
                    self.coach_type
                )
            )
        return self.trains

    def add_carriages(self, train):
        carriages = self.make_request(
            method='POST',
            resource='purchase/coaches/',
            data={
                'station_id_from': self.station_from.id,
                'station_id_till': self.station_till.id,
                'train': train.number,
                'coach_type': self.coach_type,
                'date_dep': train.date_dep_code,
            }
        ).get('coaches')
        for carriage in carriages:
            train.carriages.append(Carriage.from_dict(data=carriage))

    def add_coaches(self, train, carriage):
        coaches = self.make_request(
            method='POST',
            resource='purchase/coach/',
            data={
                'station_id_from': self.station_from.id,
                'station_id_till': self.station_till.id,
                'train': train.number,
                'coach_num': carriage.number,
                'coach_type': self.coach_type,
                'date_dep': train.date_dep_code
            }
        ).get('value', {}).get('places', {}).values()
        [carriage.coaches.extend(coach) for coach in coaches]

    def get_info(self, date_dep=None):
        if date_dep:
            self.date_dep = date_dep
            self.trains.clear()
        trains = self.get_trains()
        if trains:
            for train in trains:
                self.add_carriages(train)
                for carriage in train.carriages:
                    self.add_coaches(train, carriage)
        return self.trains
