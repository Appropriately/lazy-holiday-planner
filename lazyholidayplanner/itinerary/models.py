from django.db import models
from django.contrib.auth.models import User


class Trip(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="trip_creator")
    members = models.ManyToManyField(User)
    title = models.CharField(max_length=50)


class ItineraryItem(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    created_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)


class Flight(ItineraryItem):
    time = models.DateTimeField()
    departs_from = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)


class Note(ItineraryItem):
    text = models.CharField(max_length=500)
