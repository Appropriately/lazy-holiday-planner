from .services import GooglePlaceService
from django.views.generic import DetailView, CreateView
from django.shortcuts import get_object_or_404
from .models import Trip, VisitForm, Visit


class TripDetailView(DetailView):
    model = Trip
    template_name = 'trip.html'
    slug_field = 'unique_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_img_url'] = GooglePlaceService.get_photo(
            context['object'].destination)
        return context


class TripAddView(CreateView):
    model = Visit
    fields = ['arrival_time', 'leaving_time', 'location']
    template_name = 'visit/new.html'

    def dispatch(self, request, *args, **kwargs):
        self.trip = get_object_or_404(Trip, unique_id=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.trip = self.trip
        return super(TripAddView, self).form_valid(form)