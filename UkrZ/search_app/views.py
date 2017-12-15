from django.views import generic
from django.shortcuts import render

from .models import SearchingInfo
from .forms import StationForm, SearchForm
from .uz_interface import get_good_coaches


class AddSearchView(generic.CreateView):
    form_class = SearchForm
    template_name = 'add_search.html'


class ChangeSearchView(generic.UpdateView):
    model = SearchingInfo
    form_class = SearchForm


class IndexView(generic.View):

    def dispatch(self, request, *args, **kwargs):
        if request.method == 'GET':
            context = {
                'form': StationForm(),
            }
            return render(request, 'index.html', context)
        elif request.method == 'POST':
            data = request.POST
            station_from = data.get('station_from')
            station_till = data.get('station_till')
            date_dep = data.get('date_dep')
            coach_type = data.get('coach_type')
            SearchingInfo.objects.create(
                city_from=station_from,
                station_till=station_till,
                date_dep=date_dep,
                coach_type=coach_type
            )
            context = {
                'data': get_good_coaches(
                    station_from,
                    station_till,
                    date_dep,
                    coach_type
                )
            }
            return render(request, 'index.html', context)
