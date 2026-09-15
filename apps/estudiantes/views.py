"""Vistas del módulo de Estudiantes (Módulo 1)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, ProtectedError # 👈 ¡Importación de ProtectedError agregada aquí!

from .models import Estudiante, Colegio
from .forms import EstudianteForm, ColegioForm
from apps.auth_app.decorators import login_required_custom, admin_required


@login_required_custom
def estudiante_lista(request):
    """Lista de estudiantes con búsqueda y filtros."""
    query = request.GET.get('q', '')
    programa_id = request.GET.get('programa', '')
    estado = request.GET.get('estado', '')

    estudiantes = Estudiante.objects.select_related('programa', 'colegio').all()

    # Si es profesor, solo mostrar estudiantes de sus asignaciones
    if request.user.es_profesor and request.user.profesor:
        from apps.asignaciones.models import Matricula
        est_ids = Matricula.objects.filter(
            asignacion__profesor=request.user.profesor,
            activa=True
        ).values_list('estudiante_id', flat=True)
        estudiantes = estudiantes.filter(id__in=est_ids)

    if query:
        estudiantes = estudiantes.filter(
            Q(nombre_apellido__icontains=query) |
            Q(identificacion__icontains=query)
        )
    if programa_id:
        estudiantes = estudiantes.filter(programa_id=programa_id)
    if estado:
        estudiantes = estudiantes.filter(activo=(estado == 'activo'))

    from apps.materias.models import Programa
    programas = Programa.objects.filter(activo=True)

    return render(request, 'estudiantes/estudiante_lista.html', {
        'estudiantes': estudiantes,
        'programas': programas,
        'query': query,
        'programa_id': programa_id,
        'estado': estado,
    })


@admin_required
def estudiante_crear(request):
    """Crear un nuevo estudiante."""
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante creado exitosamente.')
            return redirect('estudiantes:lista')
    else:
        form = EstudianteForm()
    return render(request, 'estudiantes/estudiante_form.html', {
        'form': form, 'titulo': 'Registrar Estudiante', 'accion': 'Guardar'
    })


@admin_required
def estudiante_editar(request, pk):
    """Editar un estudiante existente."""
    estudiante = get_object_or_404(Estudiante, pk=pk)
    if request.method == 'POST':
        form = EstudianteForm(request.POST, instance=estudiante)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estudiante actualizado exitosamente.')
            return redirect('estudiantes:lista')
    else:
        form = EstudianteForm(instance=estudiante)
    return render(request, 'estudiantes/estudiante_form.html', {
        'form': form, 'titulo': 'Editar Estudiante', 'accion': 'Actualizar'
    })


@admin_required
def estudiante_eliminar(request, pk):
    estudiante = get_object_or_404(Estudiante, pk=pk)
    
    if request.method == 'POST':
        try:
            estudiante.delete()
            messages.success(request, 'Estudiante eliminado correctamente.')
        except ProtectedError:
            messages.error(
                request, 
                f'No se puede eliminar a {estudiante.nombre_apellido} porque tiene historial académico (asistencias, notas o matrículas) vinculado. Te recomendamos "Desactivarlo" editando su perfil.'
            )
        
        return redirect('estudiantes:lista') 

    return render(request, 'estudiantes/confirmar_eliminar.html', {'estudiante': estudiante})


# === Colegios ===
@admin_required
def colegio_lista(request):
    """Lista de colegios."""
    colegios = Colegio.objects.all()
    return render(request, 'estudiantes/colegio_lista.html', {'colegios': colegios})


@admin_required
def colegio_crear(request):
    """Crear un nuevo colegio."""
    if request.method == 'POST':
        form = ColegioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colegio creado exitosamente.')
            return redirect('estudiantes:colegio_lista')
    else:
        form = ColegioForm()
    return render(request, 'estudiantes/colegio_form.html', {
        'form': form, 'titulo': 'Registrar Colegio', 'accion': 'Guardar'
    })


@admin_required
def colegio_editar(request, pk):
    """Editar un colegio."""
    colegio = get_object_or_404(Colegio, pk=pk)
    if request.method == 'POST':
        form = ColegioForm(request.POST, instance=colegio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Colegio actualizado exitosamente.')
            return redirect('estudiantes:colegio_lista')
    else:
        form = ColegioForm(instance=colegio)
    return render(request, 'estudiantes/colegio_form.html', {
        'form': form, 'titulo': 'Editar Colegio', 'accion': 'Actualizar'
    })
