# coding: utf-8
from .uz import Direction


def get_good_coaches(station_from, station_till, date_dep, coach_type):
    direct = Direction(station_from, station_till, date_dep, coach_type)
    all_coaches = direct.get_info()
    if isinstance(all_coaches, str):
        return all_coaches
    GOOD_COACHES = list(range(5, 32, 2))
    for train in all_coaches:
        carriages = train.get('carriages')
        for carriage in carriages:
            coaches = carriage.get('coaches')
            good_coaches = list()
            for coach in coaches:
                if int(coach) in GOOD_COACHES:
                    good_coaches.append(coach)
            if good_coaches:
                carriage['coaches'] = good_coaches
            else:
                carriage.clear()
        train['carriages'] = [carriage for carriage in carriages if carriage]
    all_coaches = [train for train in all_coaches if train.get('carriages')]

    if all_coaches:
        result = ''
        for train in all_coaches:
            res = 'Поезд: {}\n'.format(train.get('train'))
            for carriage in train.get('carriages'):
                res += '\tВагон №{}, места: {}\n'.format(
                    carriage.get('number'),
                    ', '.join(carriage.get('coaches'))
                )
            res += '\n'
            result += res

    else:
        result = 'Нет поездов с хорошими местами. Попробуйте другою дату.'

    return result
