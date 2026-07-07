"""URLs del módulo de Calificaciones."""
from django.urls import path
from . import views

app_name = 'notas'

urlpatterns = [
    path('', views.seleccionar_materia_notas, name='seleccionar_materia'),
    path('<int:asignacion_id>/registrar/', views.registrar_notas, name='registrar'),
    path('<int:asignacion_id>/ver/', views.ver_notas, name='ver_notas'),
]
