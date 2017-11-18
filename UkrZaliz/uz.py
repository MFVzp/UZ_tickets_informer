# coding: utf-8
import requests


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
        self.info = list()

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
        self.trains = [train for train in trains if [type_id for type_id in train.get('types', {}) if type_id.get('id')==self.coach_type]]
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

    def get_info(self):
        self.get_trains()
        for train in self.trains:
            train_info = {
                'train': '{0} {1} - {2}'.format(
                    train.get('num'),
                    train.get('from', {}).get('station'),
                    train.get('till', {}).get('station')
                ),
                'carriages': list(),
            }
            self.get_carriages(train)
            for carriage in self.carriages[train.get('num')]:
                train_info['carriages'].append({
                    'number': carriage.get('num'),
                    'coaches': self.get_coaches_in_carriage(train, carriage)
                })
            self.info.append(train_info)
        return self.info
    

if __name__ == '__main__':
    CITY_FROM = 'Киев'
    CITY_TILL = 'Запорожье 1'
    DATE = '30.12.2017'

    direct = Direction(CITY_TILL, CITY_FROM, DATE)
    coaches = direct.get_info()
    print(coaches, '\n')
