import random

from .services import GooglePlaceService
from django.views.generic import DetailView, CreateView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic.base import TemplateView
import datetime
from django.contrib.auth.decorators import login_required
from .models import Trip, Visit
from .forms import TripAddForm


class TripDetailView(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'trip.html'
    slug_field = 'unique_id'

    def get(self, request, *args, **kwargs):
        result = super().get(request, *args, **kwargs)
        members = self.object.members.all()
        max_party_size = self.object.party_size
        if request.user in members or len(members) < max_party_size:
            self.object.members.add(request.user)
            return result
        else:
            return HttpResponseRedirect(reverse('trip_full'))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['hero_img_url'] = GooglePlaceService.get_photo(
            context['object'].destination)
        context['schedule_items'] = Visit.objects.filter(
            trip=context['object']).order_by('arrival_time')
        context['landmarks'] = random.sample(
            GooglePlaceService.get_landmarks(context['object'].destination), 3)
        return context


class TripAddView(CreateView):
    form_class = TripAddForm
    template_name = 'visit/new.html'

    def get_initial(self):
        initial = super().get_initial()
        initial = initial.copy()
        trip = Trip.objects.get(unique_id=self.kwargs['slug'])
        initial['trip'] = trip.pk
        get_params = self.request.GET
        initial['location'] = get_params.get('location')
        now = datetime.datetime.now(datetime.timezone.utc)
        initial['arrival_time'] = get_params.get('arrival_time') \
                                  or now
        later = initial['arrival_time'] + datetime.timedelta(hours=2)
        initial['leaving_time'] = get_params.get('leaving_time') \
                                  or later
        return initial

    def dispatch(self, request, *args, **kwargs):
        get_object_or_404(Trip, unique_id=kwargs['slug'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        location = form.instance.location
        destination = form.instance.trip.destination
        search_term = f"{location} near {destination}"
        form.instance.full_address = GooglePlaceService.get_full_address(
            search_term)
        return super(TripAddView, self).form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['trip_slug'] = self.kwargs.get('slug')
        return context


class TripFullView(TemplateView):
    template_name = 'trip_full.html'

@login_required
def delete(request, part_id, slug):
    visit_to_delete = Visit.objects.get(id=part_id)
    visit_to_delete.delete()
    return redirect(f'/trip/{slug}')