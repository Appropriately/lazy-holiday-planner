import uuid
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Trip(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name="trip_creator")
    members = models.ManyToManyField(User, related_name="member")
    title = models.CharField(max_length=50)
    notes = models.CharField(max_length=500,
                             default="A trip generated automatically.")
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False,
                                 unique=True)
    destination = models.CharField(max_length=100)
    party_size = models.IntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    purchase_url = models.CharField(max_length=2000)

    def __str__(self):
        return self.title

    def attendees(self):
        number_of_members = self.members.all().count()
        if number_of_members == 1:
            return f"You are going"
        elif number_of_members == 2:
            return "You and one mate are going"
        else:
            return f"You and {number_of_members} mates are going"

    def get_initial_flight(self):
        flights = Flight.objects.filter(trip=self).order_by('leaving_time')
        if flights is not None:
            return flights.first()
        else:
            return None

    def get_return_flight(self):
        flights = Flight.objects.filter(trip=self).order_by('-arrival_time')
        if flights is not None:
            return flights.first()
        else:
            return None

    def get_start_date(self):
        return "NO DATA" if self.get_initial_flight() is None else self.get_initial_flight().leaving_time

    def get_end_date(self):
        return "NO DATA" if self.get_return_flight() is None else self.get_return_flight().arrival_time


class ItineraryItem(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    arrival_time = models.DateTimeField()
    leaving_time = models.DateTimeField()

    def get_absolute_url(self):
        return ".."


class Flight(ItineraryItem):
    departs_from = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)


class Visit(ItineraryItem):
    location = models.CharField(max_length=100)
    full_address = models.CharField(max_length=200)

    def get_directions_to_link(self):
        return f"https://www.google.com/maps/dir/?api=1&origin={self.trip.destination}&destination={self.full_address}&travelmode=transit"

    def get_directions_from_link(self):
        return f"https://www.google.com/maps/dir/?api=1&origin={self.full_address}&destination={self.trip.destination}&travelmode=transit"

    def clean(self):
        fly_out_time = self.trip.get_initial_flight().arrival_time
        fly_back_time = self.trip.get_return_flight().leaving_time
        if self.arrival_time < fly_out_time:
            raise ValidationError(
                'The arrival time must be later than the flight out')
        if self.leaving_time > fly_back_time:
            raise ValidationError(
                'The leaving time must be earlier than the return flight')


class Note(ItineraryItem):
    text = models.CharField(max_length=500)
