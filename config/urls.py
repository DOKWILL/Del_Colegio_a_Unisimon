"""
URL Configuration principal del proyecto.
Enruta a cada aplicación modular del sistema.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lambda request: redirect('dashboard:index')),
    path('auth/', include('apps.auth_app.urls')),
    path('dashboard/', include('apps.dashboard.urls')),
    path('estudiantes/', include('apps.estudiantes.urls')),
    path('profesores/', include('apps.profesores.urls')),
    path('materias/', include('apps.materias.urls')),
    path('espacios/', include('apps.espacios.urls')),
    path('asignaciones/', include('apps.asignaciones.urls')),
    path('asistencia/', include('apps.asistencia.urls')),
    path('notas/', include('apps.notas.urls')),
    path('reportes/', include('apps.reportes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
