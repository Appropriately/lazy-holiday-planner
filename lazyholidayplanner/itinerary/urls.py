from django.urls import path

from . import views
from .views import TripDetailView, TripAddView

urlpatterns = [
    path('<slug:slug>/add/', TripAddView.as_view(), name='trip_schedule'),
    path('<slug>/', TripDetailView.as_view(), name='trip_detail'),
]
