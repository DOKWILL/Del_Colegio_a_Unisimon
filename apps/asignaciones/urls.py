"""URLs del módulo de Asignaciones."""
from django.urls import path
from . import views

app_name = 'asignaciones'

urlpatterns = [
    path('', views.asignacion_lista, name='lista'),
    path('crear/', views.asignacion_crear, name='crear'),
    path('<int:pk>/editar/', views.asignacion_editar, name='editar'),
    path('<int:pk>/eliminar/', views.asignacion_eliminar, name='eliminar'),
    path('<int:pk>/matricular/', views.matricular_estudiantes, name='matricular'),
    path('<int:pk>/desmatricular/<int:matricula_id>/', views.desmatricular_estudiante, name='desmatricular'),
    # Horario por docente
    path('horarios/', views.horario_docentes, name='horario_docentes'),
    path('horarios/<int:profesor_id>/', views.horario_docente_detalle, name='horario_docente_detalle'),
]
