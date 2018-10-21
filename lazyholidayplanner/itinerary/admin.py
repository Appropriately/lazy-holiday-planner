from django.contrib import admin
from .models import Trip, Visit, Flight


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    pass

@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    pass
