"""URLs del módulo de Asistencia."""
from django.urls import path
from . import views

app_name = 'asistencia'

urlpatterns = [
    path('', views.seleccionar_materia, name='seleccionar_materia'),
    path('<int:asignacion_id>/registrar/', views.registrar_asistencia, name='registrar'),
    path('<int:asignacion_id>/ver/', views.ver_asistencia, name='ver_asistencia'),
    path('<int:asignacion_id>/encuentro/<int:encuentro>/', views.detalle_encuentro, name='detalle_encuentro'),
]
