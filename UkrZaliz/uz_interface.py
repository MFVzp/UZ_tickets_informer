# coding: utf-8
from uz import Direction
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('station_from', help='Name of station from')
    parser.add_argument('station_till', help='Name of station to')
    parser.add_argument('date_dep', help='Date in format dd.mm.yyyy')
    parser.add_argument('--coach_type', default='П')

    args = parser.parse_args()

    direct = Direction(args.station_from, args.station_till, args.date_dep, args.coach_type)
    all_coaches = direct.get_info()
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
        for train in all_coaches:
            print('Поезд: {}'.format(train.get('train')))
            for carriage in train.get('carriages'):
                print('\tВагон №{}, места: {}'.format(
                    carriage.get('number'),
                    ', '.join(carriage.get('coaches'))
                ))
            print('\n')
    else:
        print('Нет поездов с хорошими местами. Попробуйте другою дату.')
