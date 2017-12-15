from django import forms
from django.contrib.auth import authenticate

from .models import MyUser


class AuthLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True}), label='Name')
    password = forms.CharField(widget=forms.PasswordInput, label='Password')

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise forms.ValidationError('You entered wrong name or password')
        return super(AuthLoginForm, self).clean(*args, **kwargs)


class AuthRegisterForm(forms.ModelForm):

    class Meta:
        model = MyUser
        fields = (
            'email',
            'username',
            'password',
            'first_name',
            'last_name',
        )
