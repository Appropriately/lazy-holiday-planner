import uuid
from django.db import models
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


class ItineraryItem(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return ".."


class Flight(ItineraryItem):
    time = models.DateTimeField()
    departs_from = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)


class Visit(ItineraryItem):
    arrival_time = models.DateTimeField()
    leaving_time = models.DateTimeField()
    location = models.CharField(max_length=200)


class Note(ItineraryItem):
    text = models.CharField(max_length=500)
