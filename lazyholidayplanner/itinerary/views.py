import random

from .services import GooglePlaceService
from django.views.generic import DetailView, CreateView
from django.shortcuts import get_object_or_404
from .models import Trip, Visit
from .forms import TripAddForm


class TripDetailView(DetailView):
    model = Trip
    template_name = 'trip.html'
    slug_field = 'unique_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_img_url'] = GooglePlaceService.get_photo(
            context['object'].destination)
        context['schedule_items'] = Visit.objects.filter(trip=context['object'])
        context['landmarks'] = random.sample(GooglePlaceService.get_landmarks(context['object'].destination),3)
        return context


class TripAddView(CreateView):
    form_class = TripAddForm
    template_name = 'visit/new.html'

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        initial['trip'] = Trip.objects.get(unique_id=self.kwargs['slug']).pk
        return initial

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Trip, unique_id=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        form.instance.trip = self.trip
        search_term = f"{form.instance.location} near {self.trip.destination}"
        form.instance.full_address = GooglePlaceService.get_full_address(search_term)
        return super(TripAddView, self).form_valid(form)
