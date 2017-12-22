# coding: utf-8
import requests
import datetime


def get_datetime_from_string(text):
    date, time = text.split()
    date = list(map(int, date.split('-')))
    time = list(map(int, time.split(':')))
    return datetime.datetime(
        year=date[0],
        month=date[1],
        day=date[2],
        hour=time[0],
        minute=time[1],
        second=time[2]
    )


class Direction:

    def __init__(self,
                 city_from,
                 city_till,
                 date_dep,
                 coach_type='П',
                 time_dep='00:00',
                 url='https://booking.uz.gov.ua/ru/'
                 ):
        self.url = url
        self.station_from = self.get_station(city_from)
        self.station_till = self.get_station(city_till)
        self.date_dep = date_dep
        self.time_dep = time_dep
        self.coach_type = coach_type
        self.carriages = dict()
        self.coaches = dict()

    def get_station(self, name):
        stations = requests.get(
            url=self.url + 'purchase/station/',
            params={'term': name},
        ).json()
        for station in stations:
            if station.get('title') == name:
                return station
        raise Exception('You are searching: "{0}". Available stations: {1}'.format(
            name,
            ', '.join(['"' + station.get('title') + '"' for station in stations])
        ))

    def get_trains(self):
        trains = requests.post(
            url=self.url + 'purchase/search/',
            data={
                'station_id_from': self.station_from.get('value'),
                'station_id_till': self.station_till.get('value'),
                'station_from': self.station_from.get('title'),
                'station_till': self.station_till.get('title'),
                'date_dep': self.date_dep,
                'time_dep': self.time_dep,
                'time_dep_till': '',
                'another_ec': 0,
                'search': '',
            }
        ).json().get('value')
        if isinstance(trains, str):
            self.info = trains
        else:
            self.info = list()
            self.trains = [train for train in trains if [type_id for type_id in train.get('types', {}) if type_id.get('id')==self.coach_type]]
            for train in self.trains:
                train['date_from'] = get_datetime_from_string(train['from']['src_date'])
                train['date_till'] = get_datetime_from_string(train['till']['src_date'])
            return self.trains

    def get_carriages(self, train):
        carriages = requests.post(
            url=self.url + 'purchase/coaches/',
            data={
                'station_id_from': self.station_from.get('value'),
                'station_id_till': self.station_till.get('value'),
                'train': train.get('num'),
                'coach_type': self.coach_type,
                'date_dep': train.get('from', {}).get('date'),
                'round_trip': 0,
                'another_ec': 0,
            }
        ).json().get('coaches')
        self.carriages[train.get('num')] = carriages
        return carriages

    def get_coaches_in_carriage(self, train, carriage):
        coaches = requests.post(
            url=self.url + 'purchase/coach/',
            data={
                'station_id_from': self.station_from.get('value'),
                'station_id_till': self.station_till.get('value'),
                'train': train.get('num'),
                'model': train.get('model'),
                'coach_num': carriage.get('num'),
                'coach_type': carriage.get('type'),
                'coach_class': carriage.get('class'),
                'date_dep': train.get('from', {}).get('date'),
            }
        ).json().get('value', {}).get('places', {}).get(list(carriage.get('prices', {}).keys())[0])
        self.coaches[(train.get('num'), carriage.get('num'))] = coaches
        return coaches

    def get_info(self, date_dep=None):
        if date_dep:
            self.date_dep = date_dep
        trains = self.get_trains()
        if trains:
            for train in self.trains:
                train_info = {
                    'train': '{0} {1} - {2}'.format(
                        train.get('num'),
                        train.get('from', {}).get('station'),
                        train.get('till', {}).get('station')
                    ),
                    'carriages': list(),
                    'date_from': train.get('date_from'),
                    'date_till': train.get('date_till'),
                }
                self.get_carriages(train)
                for carriage in self.carriages[train.get('num')]:
                    train_info['carriages'].append({
                        'number': carriage.get('num'),
                        'coaches': self.get_coaches_in_carriage(train, carriage)
                    })
                self.info.append(train_info)
        return self.info

    def get_good_coaches(self, date_dep=None):
        all_coaches = self.get_info(date_dep)
        if isinstance(all_coaches, str):
            return all_coaches
        request_coaches = list(range(5, 32, 2))
        for train in all_coaches:
            carriages = train.get('carriages')
            for carriage in carriages:
                coaches = carriage.get('coaches')
                good_coaches = list()
                for coach in coaches:
                    if int(coach) in request_coaches:
                        good_coaches.append(coach)
                if good_coaches:
                    carriage['coaches'] = good_coaches
                else:
                    carriage.clear()
            train['carriages'] = [carriage for carriage in carriages if carriage]
        all_coaches = [train for train in all_coaches if train.get('carriages')]

        return all_coaches if len(all_coaches) else False


if __name__ == '__main__':
    CITY_FROM = 'Киев'
    CITY_TILL = 'Запорожье 1'
    DATE = '30.12.2017'

    direct = Direction(CITY_TILL, CITY_FROM, DATE)
    coaches = direct.get_info()
    print(coaches, '\n')
