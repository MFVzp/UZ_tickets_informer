from django.urls import path
from .views import viber_hook


app_name = 'viber'
urlpatterns = [
    path('hook', viber_hook, name='hook'),
]
