import datetime
import random

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


CODE_LEN = 32


def get_random_code():
    population = list(map(chr, range(48, 58))) + list(map(chr, range(65, 91))) + list(map(chr, range(97, 123)))
    return ''.join(random.sample(population, CODE_LEN))


def get_now_plus_1_day():
    return timezone.now() + datetime.timedelta(days=1)


class MyUser(AbstractUser):
    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=32,
        unique=True
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=32,
        blank=True,
        null=True
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=32,
        blank=True,
        null=True
    )
    email = models.EmailField(
        verbose_name='Адрес електронной почты',
        max_length=64,
        unique=True
    )
    tel_number = models.CharField(
        verbose_name='Номер телефона',
        max_length=13,
        unique=True,
        null=True,
        blank=True
    )
    viber_id = models.CharField(
        max_length=64,
        null=True
    )
    viber_secret_message = models.CharField(
        max_length=CODE_LEN,
        default=get_random_code
    )


class Invite(models.Model):
    email = models.EmailField(verbose_name='Email пользователя')
    code = models.CharField(max_length=CODE_LEN, default=get_random_code)
    expiration_date = models.DateTimeField(default=get_now_plus_1_day)
    create_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.code
