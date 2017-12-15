from django.urls import path
from .views import *


app_name = 'search'
urlpatterns = [
    path('', SearchListView.as_view(), name='list'),
    path('add', AddSearchView.as_view(), name='add')
]
