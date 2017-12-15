# -*- coding: utf-8 -*-
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout

from .forms import AuthLoginForm, AuthRegisterForm


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
        'action_title': 'Enter',
        'action_button': 'Enter',
    }
    return render(request, 'form.html', context)


@login_required(login_url=reverse_lazy('auth:login'))
def logout_view(request):
    logout(request)
    return redirect('search:list')


def register_view(request):
    form = AuthRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        password = form.cleaned_data.get('password')
        user.set_password(password)
        user.save()
        if user is not None:
            login(request, user)
        return redirect('search:list')
    context = {
        'form': form,
        'action_title': 'Register',
        'action_button': 'Sign Up',
    }
    return render(request, 'form.html', context)
