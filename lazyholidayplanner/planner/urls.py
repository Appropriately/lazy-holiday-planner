
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    re_path(r'^api/typeform/$', views.typeform_result, name='typeform_result'),
]