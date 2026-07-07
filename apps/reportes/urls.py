"""URLs del módulo de Reportes."""
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('', views.seleccionar_materia_reporte, name='seleccionar_materia'),
    path('<int:asignacion_id>/preview/', views.vista_previa_reporte, name='vista_previa'),
    path('<int:asignacion_id>/pdf/', views.descargar_pdf, name='descargar_pdf'),
    path('<int:asignacion_id>/excel/', views.descargar_excel, name='descargar_excel'),
]
