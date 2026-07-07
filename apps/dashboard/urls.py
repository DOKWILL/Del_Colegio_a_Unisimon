"""URLs del Dashboard."""
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('filter/', views.dashboard_filter, name='filter'),
]
