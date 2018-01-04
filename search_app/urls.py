from django.urls import path
from .views import *


app_name = 'search'
urlpatterns = [
    path('', SearchListView.as_view(), name='list'),
    path('add', AddSearchView.as_view(), name='add'),
    path('instructions', InstructionsView.as_view(), name='instructions'),
    path('stop', StopSearchingView.as_view(), name='stop_search'),
    path('delete', DeleteSearchingView.as_view(), name='delete_search'),
    path('proxy_stations', ProxyStationsView.as_view(), name='proxy_stations')
]
