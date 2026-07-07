"""URLs de autenticación y gestión de usuarios."""
from django.urls import path
from . import views

app_name = 'auth_app'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('mi-password/', views.mi_password, name='mi_password'),
    path('usuarios/', views.usuario_lista, name='usuario_lista'),
    path('usuarios/crear/', views.usuario_crear, name='usuario_crear'),
    path('usuarios/<int:pk>/editar/', views.usuario_editar, name='usuario_editar'),
    path('usuarios/<int:pk>/eliminar/', views.usuario_eliminar, name='usuario_eliminar'),
    path('usuarios/<int:pk>/password/', views.cambiar_password, name='cambiar_password'),
    path('usuarios/<int:pk>/bloquear/', views.bloquear_usuario, name='bloquear_usuario'),
    path('configuracion/', views.configuracion_view, name='configuracion'),
]
