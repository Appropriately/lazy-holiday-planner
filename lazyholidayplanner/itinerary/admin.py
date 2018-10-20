from django.contrib import admin
from .models import Trip, Visit


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    pass


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    pass
