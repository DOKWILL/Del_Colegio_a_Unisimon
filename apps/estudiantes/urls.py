"""URLs del módulo de Estudiantes."""
from django.urls import path
from . import views

app_name = 'estudiantes'

urlpatterns = [
    path('', views.estudiante_lista, name='lista'),
    path('crear/', views.estudiante_crear, name='crear'),
    path('<int:pk>/editar/', views.estudiante_editar, name='editar'),
    path('<int:pk>/eliminar/', views.estudiante_eliminar, name='eliminar'),
    path('colegios/', views.colegio_lista, name='colegio_lista'),
    path('colegios/crear/', views.colegio_crear, name='colegio_crear'),
    path('colegios/<int:pk>/editar/', views.colegio_editar, name='colegio_editar'),
]
