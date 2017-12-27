# coding: utf-8
from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from .models import SearchingInfo
from .forms import SearchForm
from .tasks import looking_for_coaches


MAX_ACTIVE_SEARCHES_PER_USER = 3


class SearchListView(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy('auth:login')
    model = SearchingInfo
    template_name = 'searching_list.html'
    context_object_name = 'search_list'

    def get_queryset(self):
        queryset = SearchingInfo.objects.filter(
            author=self.request.user
        ).select_related('fail_result').prefetch_related('success_results')
        return queryset


class AddSearchView(LoginRequiredMixin, generic.CreateView):
    login_url = reverse_lazy('auth:login')
    form_class = SearchForm
    template_name = 'add_search.html'
    success_url = reverse_lazy('search:list')

    def form_valid(self, form):
        user = self.request.user
        active_user_searches = SearchingInfo.objects.filter(
            author=self.request.user,
            is_actual=True
        )
        if len(active_user_searches) >= MAX_ACTIVE_SEARCHES_PER_USER:
            return HttpResponse('Вы достигли максимального чиста активных запросов'.encode())
        else:
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            looking_for_coaches.delay(instance.id)
            return super(AddSearchView, self).form_valid(form)
