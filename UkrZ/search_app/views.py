from django.views import generic
from django.shortcuts import render

from .forms import StationForm
from UkrZaliz.uz_interface import get_good_coaches


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
            context = {
                'data': get_good_coaches(
                    station_from,
                    station_till,
                    date_dep,
                    coach_type
                )
            }
            return render(request, 'index.html', context)
