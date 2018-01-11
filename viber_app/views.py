# coding: utf-8
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.messages import TextMessage


viber = Api(BotConfiguration(
    name='Hooker bot',
    avatar='http://viber.com/avatar.jpg',
    auth_token=settings.VIBER_AUTH_TOKEN
))


@csrf_exempt
def viber_hook(request):
    viber_request = viber.parse_request(request.body.decode())
    if isinstance(viber_request, ViberMessageRequest):
        try:
            user = get_user_model().objects.get(viber_secret_message=viber_request.message.text, viber_id=None)
            user.viber_id = viber_request.sender.id
            user.save()
            viber.send_messages(
                to=viber_request.sender.id,
                messages=[
                    TextMessage(
                        text='Вы зарегистрированны. Теперь вы будете получать результаты поиска и через Viber.'
                    ),
                ]
            )
        except ObjectDoesNotExist:
            pass
    return HttpResponse()
