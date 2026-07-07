"""URLs del módulo de Materias y Programas."""
from django.urls import path
from . import views

app_name = 'materias'

urlpatterns = [
    path('', views.materia_lista, name='lista'),
    path('crear/', views.materia_crear, name='crear'),
    path('<int:pk>/editar/', views.materia_editar, name='editar'),
    path('<int:pk>/eliminar/', views.materia_eliminar, name='eliminar'),
    path('programas/', views.programa_lista, name='programa_lista'),
    path('programas/crear/', views.programa_crear, name='programa_crear'),
    path('programas/<int:pk>/editar/', views.programa_editar, name='programa_editar'),
]
