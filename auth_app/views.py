# -*- coding: utf-8 -*-
from enum import Enum

from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.db import transaction
from django.template.loader import render_to_string
from django.conf import settings

from .forms import AuthLoginForm, AuthRegisterForm, InviteForm, AuthEditForm
from .models import Invite
from search_app.tasks import mail_to
from viber_app.tasks import send_viber_message


class Action(Enum):
    LOGIN = 'Войти'
    REGISTER = 'Зарегистрироваться'
    INVITE = 'Пригласить'
    EDIT = 'Изменить профиль'


def invite_view(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden('Вы не властны сделать это.')
    form = InviteForm(request.POST or None)
    if form.is_valid():
        invite = form.save()
        context = {
            'invite_uri': '{}?code={}'.format(
                request.build_absolute_uri(location=reverse('auth:register')),
                invite.code
            )
        }
        mail_to.delay(
            subject='Приглашение на регистрацию.',
            message=render_to_string('invite.txt', context=context, ),
            recipient_list=[invite.email, ],
            html_message=render_to_string('invite.html', context=context, )
        )
        return redirect('search:list')
    context = {
        'form': form,
        'action': Action.INVITE.value,
    }
    return render(request, 'form.html', context)


def login_view(request):
    next_url = request.GET.get('next')
    form = AuthLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(request=request, username=username, password=password)
        if user is not None:
            login(request, user)
            if next_url:
                return redirect(next_url)
        return redirect('search:list')
    context = {
        'form': form,
        'action': Action.LOGIN.value,
    }
    return render(request, 'form.html', context)


@login_required(login_url=reverse_lazy('auth:login'))
def logout_view(request):
    logout(request)
    return redirect('search:list')


def register_view(request):
    code = request.GET.get('code') or request.POST.get('code')
    if not code:
        return HttpResponseForbidden('Регистрация возможна только для приглашенных пользователей.')
    try:
        invite = Invite.objects.get(code=code)
    except ObjectDoesNotExist:
        return HttpResponseForbidden('Вы ввели неверный код приглашения.')
    if invite.expiration_date < timezone.now():
        return HttpResponseForbidden('Ваш код приглашения истек.')

    form = AuthRegisterForm(
        request.POST or None,
        initial={
            'email': invite.email,
        }
    )
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get('password')
        user.set_password(password)
        with transaction.atomic():
            user.save()
            invite.delete()
        send_viber_message.delay(
            viber_user_id=settings.SUPERUSER_VIBER_ID,
            text='User {} with number {} was registered.'.format(
                user,
                user.tel_number
            )
        )
        if user is not None:
            login(request, user)
        return redirect('search:list')
    context = {
        'code': code,
        'form': form,
        'action': Action.REGISTER.value,
    }
    return render(request, 'form.html', context)


@login_required(login_url=reverse_lazy('auth:login'))
def edit_profile_view(request):
    form = AuthEditForm(
        request.POST or None,
        instance=request.user
    )
    if form.is_valid():
        user = form.save()
        return redirect('search:list')
    context = {
        'form': form,
        'action': Action.EDIT.value,
    }
    return render(request, 'form.html', context)
