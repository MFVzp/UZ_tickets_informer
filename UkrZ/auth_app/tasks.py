# coding: utf-8
from django.utils import timezone

from UkrZ.celery import app
from .models import Invite


@app.task
def clean_expired_invites():
    expired_invites = Invite.objects.filter(expiration_date__lte=timezone.now()).delete()
    return '{}: {} expired invites is deleted.'.format(timezone.now(), expired_invites[0])

