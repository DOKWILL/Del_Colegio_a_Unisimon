"""
Decoradores de control de acceso por roles.

Provee decoradores reutilizables para proteger vistas según el rol del usuario:
- @login_required_custom: Verifica autenticación y que la cuenta no esté bloqueada
- @admin_required: Solo permite acceso a administradores
- @profesor_required: Solo permite acceso a profesores
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def login_required_custom(view_func):
    """Verifica que el usuario esté autenticado y no bloqueado."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debe iniciar sesión para acceder.')
            return redirect('auth_app:login')
        if request.user.bloqueado:
            messages.error(request, 'Su cuenta ha sido bloqueada. Contacte al administrador.')
            return redirect('auth_app:login')
        # Forzar cambio de contraseña (excepto en la vista mi_password)
        if request.user.debe_cambiar_password and request.resolver_match.url_name != 'mi_password':
            messages.warning(request, 'Debe cambiar su contraseña antes de continuar.')
            return redirect('auth_app:mi_password')
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Solo permite acceso a usuarios con rol Administrador."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debe iniciar sesión para acceder.')
            return redirect('auth_app:login')
        if request.user.bloqueado:
            messages.error(request, 'Su cuenta ha sido bloqueada.')
            return redirect('auth_app:login')
        if not request.user.es_admin:
            messages.error(request, 'No tiene permisos para acceder a esta sección.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper


def profesor_required(view_func):
    """Solo permite acceso a usuarios con rol Profesor."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, 'Debe iniciar sesión para acceder.')
            return redirect('auth_app:login')
        if request.user.bloqueado:
            messages.error(request, 'Su cuenta ha sido bloqueada.')
            return redirect('auth_app:login')
        if not request.user.es_profesor:
            messages.error(request, 'No tiene permisos para acceder a esta sección.')
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return wrapper
