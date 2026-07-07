"""
Vistas de autenticación y gestión de usuarios (Módulo 9).

Incluye: login, logout, CRUD de usuarios, cambio de contraseña,
bloqueo/desbloqueo de cuentas y configuración del sistema.
"""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Q

from .models import Usuario, Rol, ConfiguracionSistema
from .forms import (
    LoginForm, UsuarioCreateForm, UsuarioEditForm,
    CambiarPasswordForm, ConfiguracionForm, MiPasswordForm
)
from .decorators import login_required_custom, admin_required

logger = logging.getLogger('apps')


# ==============================================================================
# AUTENTICACIÓN
# ==============================================================================

def login_view(request):
    """Vista de inicio de sesión."""
    if request.user.is_authenticated:
        if request.user.debe_cambiar_password:
            return redirect('auth_app:mi_password')
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.bloqueado:
                messages.error(request, 'Su cuenta ha sido bloqueada. Contacte al administrador.')
                return render(request, 'auth_app/login.html', {'form': form})
            login(request, user)
            logger.info(f"Usuario '{user.username}' inició sesión.")
            # Si debe cambiar contraseña, redirigir a cambio obligatorio
            if user.debe_cambiar_password:
                messages.warning(
                    request,
                    'Debe cambiar su contraseña antes de continuar.'
                )
                return redirect('auth_app:mi_password')
            messages.success(request, f'Bienvenido(a), {user.get_full_name() or user.username}')
            return redirect('dashboard:index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'auth_app/login.html', {'form': form})


def logout_view(request):
    """Vista de cierre de sesión."""
    logger.info(f"Usuario '{request.user.username}' cerró sesión.")
    logout(request)
    messages.info(request, 'Ha cerrado sesión correctamente.')
    return redirect('auth_app:login')


@login_required_custom
def mi_password(request):
    """
    Vista para que el usuario cambie su propia contraseña.
    Obligatorio en el primer inicio de sesión (debe_cambiar_password=True).
    """
    if request.method == 'POST':
        form = MiPasswordForm(request.POST)
        if form.is_valid():
            # Verificar contraseña actual
            if not request.user.check_password(form.cleaned_data['password_actual']):
                messages.error(request, 'La contraseña actual es incorrecta.')
            else:
                request.user.set_password(form.cleaned_data['nueva_password'])
                request.user.debe_cambiar_password = False
                request.user.save()
                # Re-autenticar para mantener la sesión
                login(request, request.user)
                logger.info(f"Usuario '{request.user.username}' cambió su contraseña.")
                messages.success(request, '¡Contraseña actualizada exitosamente!')
                return redirect('dashboard:index')
    else:
        form = MiPasswordForm()

    return render(request, 'auth_app/mi_password.html', {
        'form': form,
        'es_obligatorio': request.user.debe_cambiar_password,
    })


# ==============================================================================
# CRUD DE USUARIOS
# ==============================================================================

@admin_required
def usuario_lista(request):
    """Lista de todos los usuarios del sistema."""
    query = request.GET.get('q', '')
    usuarios = Usuario.objects.select_related('rol', 'profesor').all()
    if query:
        usuarios = usuarios.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    return render(request, 'auth_app/usuario_lista.html', {
        'usuarios': usuarios,
        'query': query,
    })


@admin_required
def usuario_crear(request):
    """Crear un nuevo usuario."""
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f"Admin '{request.user.username}' creó usuario '{user.username}'.")
            messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
            return redirect('auth_app:usuario_lista')
    else:
        form = UsuarioCreateForm()

    return render(request, 'auth_app/usuario_form.html', {
        'form': form,
        'titulo': 'Crear Usuario',
        'accion': 'Guardar',
    })


@admin_required
def usuario_editar(request, pk):
    """Editar un usuario existente."""
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = UsuarioEditForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            logger.info(f"Admin '{request.user.username}' editó usuario '{usuario.username}'.")
            messages.success(request, f'Usuario "{usuario.username}" actualizado exitosamente.')
            return redirect('auth_app:usuario_lista')
    else:
        form = UsuarioEditForm(instance=usuario)

    return render(request, 'auth_app/usuario_form.html', {
        'form': form,
        'titulo': 'Editar Usuario',
        'accion': 'Actualizar',
        'usuario': usuario,
    })


@admin_required
def usuario_eliminar(request, pk):
    """Eliminar un usuario."""
    usuario = get_object_or_404(Usuario, pk=pk)
    if request.method == 'POST':
        username = usuario.username
        usuario.delete()
        logger.info(f"Admin '{request.user.username}' eliminó usuario '{username}'.")
        messages.success(request, f'Usuario "{username}" eliminado exitosamente.')
        return redirect('auth_app:usuario_lista')
    return render(request, 'auth_app/usuario_confirmar_eliminar.html', {
        'usuario': usuario,
    })


@admin_required
def cambiar_password(request, pk):
    """Cambiar la contraseña de un usuario."""
    usuario = get_object_or_404(Usuario, pk=pk)

    if request.method == 'POST':
        form = CambiarPasswordForm(request.POST)
        if form.is_valid():
            usuario.set_password(form.cleaned_data['nueva_password'])
            usuario.debe_cambiar_password = True
            usuario.save()
            logger.info(f"Admin cambió contraseña de '{usuario.username}'.")
            messages.success(request, f'Contraseña de "{usuario.username}" cambiada. El usuario deberá cambiarla al iniciar sesión.')
            return redirect('auth_app:usuario_lista')
    else:
        form = CambiarPasswordForm()

    return render(request, 'auth_app/cambiar_password.html', {
        'form': form,
        'usuario': usuario,
    })


@admin_required
def bloquear_usuario(request, pk):
    """Bloquear/desbloquear un usuario."""
    usuario = get_object_or_404(Usuario, pk=pk)
    usuario.bloqueado = not usuario.bloqueado
    usuario.save()
    estado = 'bloqueado' if usuario.bloqueado else 'desbloqueado'
    logger.info(f"Admin '{request.user.username}' {estado} usuario '{usuario.username}'.")
    messages.success(request, f'Usuario "{usuario.username}" {estado} exitosamente.')
    return redirect('auth_app:usuario_lista')


# ==============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ==============================================================================

@admin_required
def configuracion_view(request):
    """Configuración del sistema (nota mínima aprobatoria, etc.)."""
    nota_minima = ConfiguracionSistema.get_nota_minima()

    if request.method == 'POST':
        form = ConfiguracionForm(request.POST)
        if form.is_valid():
            obj, created = ConfiguracionSistema.objects.update_or_create(
                clave='nota_minima_aprobatoria',
                defaults={
                    'valor': str(form.cleaned_data['nota_minima']),
                    'descripcion': 'Nota mínima para aprobar una materia (escala 0-5)',
                }
            )
            logger.info(f"Configuración actualizada: nota mínima = {obj.valor}")
            messages.success(request, 'Configuración actualizada exitosamente.')
            return redirect('auth_app:configuracion')
    else:
        form = ConfiguracionForm(initial={'nota_minima': nota_minima})

    return render(request, 'auth_app/configuracion.html', {
        'form': form,
        'nota_minima': nota_minima,
    })
