from django.urls import path

from .views import *


app_name = 'auth'
urlpatterns = [
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('invite/', invite_view, name='invite')
]
