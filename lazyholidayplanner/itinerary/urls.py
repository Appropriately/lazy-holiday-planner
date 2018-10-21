from django.urls import path

from . import views
from .views import TripDetailView, TripAddView, TripFullView

urlpatterns = [
    path('<slug:slug>/add/', TripAddView.as_view(), name='trip_schedule'),
    path('<slug>/', TripDetailView.as_view(), name='trip_detail'),
    path('full', TripFullView.as_view(),
         name='trip_full'),
    path('delete/<part_id>/<slug:slug>/', views.delete, name='delete_view'),

]
