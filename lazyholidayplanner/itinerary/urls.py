from django.urls import path
from .views import TripDetailView

urlpatterns = [
    path('<slug>/', TripDetailView.as_view(), name='trip_detail'),
]
