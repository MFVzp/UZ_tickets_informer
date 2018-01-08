"""
Django settings for UkrZ project.

Generated by 'django-admin startproject' using Django 2.0.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os
import datetime
import typing as t
import json

import dj_database_url

from .celery import app

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

ALLOWED_HOSTS = [
    '*'
]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'search_app',
    'auth_app',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'UkrZ.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates/search_app'),
            os.path.join(BASE_DIR, 'templates/auth_app'),
            os.path.join(BASE_DIR, 'templates/mails'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'UkrZ.wsgi.application'


# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'auth_app.MyUser'


# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, 'static_files')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'

# UkrZ settings

UZ_HOST = 'https://booking.uz.gov.ua/ru/'


# Celery configurations

app.conf.beat_schedule = {
    'clear-expired-invites-every-day': {
        'task': 'auth_app.tasks.clean_expired_invites',
        'schedule': datetime.timedelta(days=1),
    },
    'clear-past-searching-info-every-day': {
        'task': 'search_app.tasks.clean_past_searching_info',
        'schedule': datetime.timedelta(days=1),
    },
}


def get_envvar(envvar: str, envtype: t.Any, required: bool = False, default: t.Any = None) -> t.Any:
    try:
        if envtype == bool:
            if os.getenv(envvar):
                value = True if os.getenv(envvar) == 'true' else False
            else:
                value = default
        elif envtype == dict:
            value = json.loads(os.getenv(envvar)) if os.getenv(envvar) else default
        else:
            value = envtype(os.getenv(envvar)) if os.getenv(envvar) else default
    except ValueError:
        if required:
            raise ValueError('Config variable {} can\'t be assigned with type {}'.format(envvar, envtype))
    else:
        if value is None and required:
            raise ValueError('Config variable {} is required'.format(envvar))
        return value


# ENV Settings

ENV = get_envvar('ENV', str)
if ENV == 'PROD':
    from prod_settings import *
elif ENV == 'DEV':
    from dev_settings import *
elif ENV == 'TEST':
    from test_settings import *
else:

    # SECURITY WARNING: keep the secret key used in production secret!
    SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '0u!z2*zq9$&q!!e=jyp7=_+iv58rl3&w@iron74($ymx*opjp&')

    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = bool(os.environ.get('DJANGO_DEBUG', True))

    # Database
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    db_from_env = dj_database_url.config()
    DATABASES['default'].update(db_from_env)

    EMAIL_HOST = get_envvar('EMAIL_HOST', str, required=True)
    EMAIL_HOST_USER = get_envvar('EMAIL_HOST_USER', str, required=True)
    EMAIL_HOST_PASSWORD = get_envvar('EMAIL_HOST_PASSWORD', str, required=True)
    EMAIL_PORT = get_envvar('EMAIL_PORT', int, required=True)
    EMAIL_USE_TLS = get_envvar('EMAIL_USE_TLS', str, default=True)
    MAX_ACTIVE_SEARCHES_PER_USER = get_envvar('MAX_ACTIVE_SEARCHES_PER_USER', int, required=True)
    VIBER_AUTH_TOKEN = get_envvar('VIBER_AUTH_TOKEN', str, required=True)
    SUPERUSER_VIBER_ID = get_envvar('SUPERUSER_VIBER_ID', str, required=True)
    CELERY_BROKER = get_envvar('CELERY_BROKER', str, default='amqp://')
