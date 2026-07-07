from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    """Configuración de la aplicación de autenticación y usuarios."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth_app'
    verbose_name = 'Autenticación y Usuarios'
