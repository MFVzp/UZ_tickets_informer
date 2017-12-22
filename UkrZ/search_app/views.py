from django.views import generic
from django.urls import reverse_lazy

from .models import SearchingInfo
from .forms import SearchForm
from .tasks import looking_for_coaches


class SearchListView(generic.ListView):
    model = SearchingInfo
    template_name = 'searching_list.html'
    context_object_name = 'search_list'


class AddSearchView(generic.CreateView):
    form_class = SearchForm
    template_name = 'add_search.html'
    success_url = reverse_lazy('search:list')

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.author = self.request.user
        instance.save()
        looking_for_coaches.delay(instance.id)
        return super(AddSearchView, self).form_valid(form)
