from django.views.generic import DetailView
from .models import Trip


class TripDetailView(DetailView):
    model = Trip
    template_name = 'trip.html'
