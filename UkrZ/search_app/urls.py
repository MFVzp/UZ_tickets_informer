from django.urls import path
from .views import IndexView


app_name = 'search'
urlpatterns = [
    path('', IndexView.as_view(), name='search_list'),
    path('add', IndexView.as_view(), name='add_search')
]
