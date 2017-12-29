# coding: utf-8
import datetime
import time
import math
import copy

import requests


GOOD_NUMBERS = list(range(5, 32, 2))


class TrainException(Exception):
    """
    Raise it when request return error.
    """


class Station:

    def __init__(self, direction, name: str):
        stations = Direction._make_request(
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
        return '{} {} - {}'.format(
            self.number,
            self.end_station_from,
            self.end_station_till
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
        return self.number


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
        self.trains_with_good_coaches = list()

    def __str__(self):
        return 'Направление {} - {} | Дата: {} | Тип мест: {}'.format(
            self.station_from,
            self.station_till,
            self.date_dep,
            self.coach_type
        )

    def _make_request(self, resource, data=None, params=None, method='GET', headers=None):
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

    def _get_trains(self):
        trains = self._make_request(
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

    def _add_carriages(self, train):
        carriages = self._make_request(
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

    def _add_coaches(self, train, carriage):
        coaches = self._make_request(
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

    @staticmethod
    def _sum_of_odds(numbers_list):
        if len(numbers_list) > 1:
            res = 0
            for i in range(len(numbers_list[:-1])):
                res += numbers_list[i + 1] - numbers_list[i]
            return res
        return 0

    @staticmethod
    def _get_best(coaches_list, amount):
        the_best_combination = {
            'combination': (0, 0),
            'difference': math.inf
        }
        for i in range(len(coaches_list[:len(coaches_list) + 1 - amount])):
            combination = (coaches_list[i:i + amount], (i, i + amount))
            difference_between_coaches = Direction._sum_of_odds(list(map(int, combination[0])))
            if difference_between_coaches < the_best_combination['difference']:
                the_best_combination['combination'] = combination[1]
                the_best_combination['difference'] = difference_between_coaches
        return the_best_combination

    def run(self, date_dep=None):
        self.trains.clear()
        self.trains_with_good_coaches.clear()
        if date_dep:
            self.date_dep = date_dep
        trains = self._get_trains()
        if trains:
            for train in trains:
                self._add_carriages(train)
                for carriage in train.carriages:
                    self._add_coaches(train, carriage)

    def get_trains(self, amount: int=0, get_good: bool=False, get_best: bool=False):
        if get_good:
            self.trains_with_good_coaches = copy.deepcopy(self.trains)

            for train_i in reversed(range(len(self.trains))):
                for carriage_i in reversed(range(len(self.trains[train_i].carriages))):
                    for coach_i in reversed(range(len(self.trains[train_i].carriages[carriage_i].coaches))):
                        if int(self.trains[train_i].carriages[carriage_i].coaches[coach_i]) not in GOOD_NUMBERS:
                            self.trains_with_good_coaches[train_i].carriages[carriage_i].coaches.pop(coach_i)
                    carriage = self.trains_with_good_coaches[train_i].carriages[carriage_i]
                    if not carriage.coaches or (len(carriage.coaches) < amount):
                        self.trains_with_good_coaches[train_i].carriages.pop(carriage_i)
                train = self.trains_with_good_coaches[train_i]
                if not train.carriages:
                    self.trains_with_good_coaches.pop(train_i)

            if get_best:
                for train_i in reversed(range(len(self.trains_with_good_coaches))):
                    train = self.trains_with_good_coaches[train_i]
                    train_best_combination = {
                        'carriage_i': 0,
                        'difference': math.inf
                    }
                    for carriage_i in reversed(range(len(train.carriages))):
                        carriage = train.carriages[carriage_i]
                        carriage_best_combination = Direction._get_best(
                            carriage.coaches,
                            amount
                        )
                        combination = carriage_best_combination['combination']
                        carriage.coaches = carriage.coaches[combination[0]:combination[1]]
                        if carriage_best_combination['difference'] < train_best_combination['difference']:
                            train_best_combination['carriage_i'] = carriage_i
                            train_best_combination['difference'] = carriage_best_combination['difference']
                    best_carriage_index = train_best_combination['carriage_i']
                    train.carriages = train.carriages[best_carriage_index:best_carriage_index+1]
            return self.trains_with_good_coaches
        return self.trains

    def get_info(self):
        return self.__str__()
