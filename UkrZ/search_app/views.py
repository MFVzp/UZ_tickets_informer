from django.views import generic
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import SearchingInfo
from .forms import SearchForm
from .tasks import looking_for_coaches


class SearchListView(LoginRequiredMixin, generic.ListView):
    login_url = reverse_lazy('auth:login')
    model = SearchingInfo
    template_name = 'searching_list.html'
    context_object_name = 'search_list'

    def get_queryset(self):
        queryset = SearchingInfo.objects.filter(
            author=self.request.user
        ).prefetch_related('results')
        return queryset


class AddSearchView(LoginRequiredMixin, generic.CreateView):
    login_url = reverse_lazy('auth:login')
    form_class = SearchForm
    template_name = 'add_search.html'
    success_url = reverse_lazy('search:list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        looking_for_coaches.delay(instance.id)
        return super(AddSearchView, self).form_valid(form)
