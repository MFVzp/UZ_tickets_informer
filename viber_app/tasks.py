# coding: utf-8
from django.contrib.auth import get_user_model
from django.conf import settings
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import TextMessage

from UkrZ.celery import app


@app.task
def send_viber_message(text, user_id=None, viber_user_id=None):
    if not viber_user_id:
        if user_id:
            user = get_user_model().objects.get(id=user_id)
            viber_user_id = user.viber_id
            if not viber_user_id:
                raise ValueError('User with id={} does not have viber id.'.format(user_id))
    viber = Api(
        BotConfiguration(
            name='Ticket bot',
            avatar='http://viber.com/avatar.jpg',
            auth_token=settings.VIBER_AUTH_TOKEN
        )
    )
    viber.send_messages(
        to=viber_user_id,
        messages=[
            TextMessage(
                text=text
            ),
        ]
    )
