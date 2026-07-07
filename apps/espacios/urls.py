"""URLs del módulo de Espacios Físicos."""
from django.urls import path
from . import views

app_name = 'espacios'

urlpatterns = [
    path('sedes/', views.sede_lista, name='sede_lista'),
    path('sedes/crear/', views.sede_crear, name='sede_crear'),
    path('sedes/<int:pk>/editar/', views.sede_editar, name='sede_editar'),
    path('aulas/', views.aula_lista, name='aula_lista'),
    path('aulas/crear/', views.aula_crear, name='aula_crear'),
    path('aulas/<int:pk>/editar/', views.aula_editar, name='aula_editar'),
]
