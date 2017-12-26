import datetime
import math

from django.core.mail import send_mail


def mail_to(text, address):
    # send_mail(
    #     subject='Success',
    #     message=text,
    #     from_email='from@example.com',
    #     recipient_list=[address, ]
    # )
    print('I sent email({}) to address {}. Work is done.'.format(
        text,
        address
    ))


def get_date_from_string(date_text):
    date = list(map(int, date_text.split('.')))
    return datetime.date(date[-1], date[-2], date[-3])


def sum_of_odds(numbers_list):
    res = 0
    for i in range(len(numbers_list[:-1])):
        res += numbers_list[i+1] - numbers_list[i]
    return res


def get_best_of_the_best(coaches_list, amount):
    the_best_combination = [[], math.inf]
    for i in range(len(coaches_list[:len(coaches_list) + 1 - amount])):
        combination = coaches_list[i:i+amount]
        difference_between_coaches = sum_of_odds(list(map(int, combination)))
        if difference_between_coaches < the_best_combination[1]:
            the_best_combination = [combination, difference_between_coaches]
    return the_best_combination
