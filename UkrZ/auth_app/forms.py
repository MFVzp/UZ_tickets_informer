# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import MyUser, Invite


class InviteForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ('email', )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        invites = Invite.objects.filter(email=email)
        if invites.exists():
            for invite in invites:
                if invite.expiration_date > timezone.now():
                    raise forms.ValidationError('Приглашение на данный email уже выслано.')
        users = get_user_model().objects.filter(email=email)
        if users.exists():
            raise forms.ValidationError('Пользователь с данным email уже зарегистрирован.')
        return email


class AuthLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}), label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('Вы ввели неверное имя пользователя или пароль.')
        return super(AuthLoginForm, self).clean()


class AuthRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput, label='Подтверждение пароля')

    class Meta:
        model = MyUser
        fields = (
            'email',
            'username',
            'password',
            'password2',
            'first_name',
            'last_name',
        )

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if len(password) < 7:
            raise forms.ValidationError("Минимальная длинна пароля - 7 символов.")

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Пароли не совпадают")
        return password2

    def save(self, commit=True):
        user = super(AuthRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
