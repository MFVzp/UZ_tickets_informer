# coding: utf-8
import requests

from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseBadRequest, JsonResponse
from django.conf import settings
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from .models import SearchingInfo, FailResult
from .forms import SearchForm
from .tasks import looking_for_coaches


class SearchListView(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy('auth:login')
    model = SearchingInfo
    template_name = 'searching_list.html'
    context_object_name = 'search_list'
    paginate_by = 3

    def get_queryset(self):
        queryset = SearchingInfo.objects.filter(
            author=self.request.user
        ).select_related(
            'fail_result'
        ).prefetch_related('success_results').prefetch_related('success_results__carriages')
        return queryset


class AddSearchView(LoginRequiredMixin, generic.CreateView):
    login_url = reverse_lazy('auth:login')
    form_class = SearchForm
    template_name = 'add_search.html'
    success_url = reverse_lazy('search:list')

    def form_valid(self, form):
        user = self.request.user
        active_user_searches = SearchingInfo.objects.filter(
            author=user,
            is_actual=True
        )
        if active_user_searches.count() >= int(settings.MAX_ACTIVE_SEARCHES_PER_USER):
            return HttpResponse('Вы достигли максимального чиста активных запросов'.encode())
        else:
            instance = form.save(commit=False)
            instance.author = user
            instance.save()
            looking_for_coaches.delay(instance.id)
            return super(AddSearchView, self).form_valid(form)


class InstructionsView(LoginRequiredMixin, generic.TemplateView):
    login_url = reverse_lazy('auth:login')
    success_url = reverse_lazy('search:list')
    template_name = 'instructions.html'

    def get_context_data(self, **kwargs):
        context = super(InstructionsView, self).get_context_data()
        context['amount_of_searching'] = settings.MAX_ACTIVE_SEARCHES_PER_USER
        return context


class StopSearchingView(generic.View):

    def post(self, *args, **kwargs):
        try:
            searching_info = SearchingInfo.objects.get(id=self.request.POST.get('id'))
        except ObjectDoesNotExist:
            return HttpResponseBadRequest
        with transaction.atomic():
            FailResult.objects.get_or_create(
                searching_info=searching_info,
                fail_message='Вы остановили данный поиск.'
            )
            searching_info.is_actual = False
            searching_info.save()
        return redirect('search:list')


class DeleteSearchingView(generic.View):

    def post(self, *args, **kwargs):
        try:
            searching_info = SearchingInfo.objects.get(id=self.request.POST.get('id'))
            searching_info.delete()
        except ObjectDoesNotExist:
            return HttpResponseBadRequest
        return redirect('search:list')


class ProxyStationsView(LoginRequiredMixin, generic.View):

    def get(self, *args, **kwargs):
        if self.request.is_ajax():
            response = requests.get(settings.UZ_HOST + 'purchase/station/?' + self.request.META.get('QUERY_STRING')).json()
            return JsonResponse(response, safe=False)
        else:
            return HttpResponseForbidden()
