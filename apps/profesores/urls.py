"""URLs del módulo de Profesores."""
from django.urls import path
from . import views

app_name = 'profesores'

urlpatterns = [
    path('', views.profesor_lista, name='lista'),
    path('crear/', views.profesor_crear, name='crear'),
    path('<int:pk>/editar/', views.profesor_editar, name='editar'),
    path('<int:pk>/eliminar/', views.profesor_eliminar, name='eliminar'),
]
