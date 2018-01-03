# coding: utf-8
import os

from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.viber_requests import ViberMessageRequest


viber = Api(BotConfiguration(
    name='PythonSampleBot',
    avatar='http://viber.com/avatar.jpg',
    auth_token=os.environ.get('VIBER_TOKEN')
))


@csrf_exempt
def viber_hook(request):
    viber_request = viber.parse_request(request.body.decode())
    if isinstance(viber_request, ViberMessageRequest):
        try:
            user = get_user_model().objects.get(viber_secret_message=viber_request.message.text, viber_id=None)
            user.viber_id = viber_request.sender.id
            user.save()
        except ObjectDoesNotExist:
            pass
    return HttpResponse()
