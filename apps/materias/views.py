"""Vistas del módulo de Materias y Programas (Módulo 3)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Materia, Programa
from .forms import MateriaForm, ProgramaForm
from apps.auth_app.decorators import admin_required


@admin_required
def materia_lista(request):
    query = request.GET.get('q', '')
    materias = Materia.objects.select_related('programa').all()
    if query:
        materias = materias.filter(
            Q(nombre__icontains=query) | Q(codigo__icontains=query)
        )
    return render(request, 'materias/materia_lista.html', {
        'materias': materias, 'query': query
    })


@admin_required
def materia_crear(request):
    if request.method == 'POST':
        form = MateriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia creada exitosamente.')
            return redirect('materias:lista')
    else:
        form = MateriaForm()
    return render(request, 'materias/materia_form.html', {
        'form': form, 'titulo': 'Registrar Materia', 'accion': 'Guardar'
    })


@admin_required
def materia_editar(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        form = MateriaForm(request.POST, instance=materia)
        if form.is_valid():
            form.save()
            messages.success(request, 'Materia actualizada exitosamente.')
            return redirect('materias:lista')
    else:
        form = MateriaForm(instance=materia)
    return render(request, 'materias/materia_form.html', {
        'form': form, 'titulo': 'Editar Materia', 'accion': 'Actualizar'
    })


@admin_required
def materia_eliminar(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        materia.delete()
        messages.success(request, 'Materia eliminada exitosamente.')
        return redirect('materias:lista')
    return render(request, 'materias/materia_confirmar_eliminar.html', {'materia': materia})


# === Programas ===
@admin_required
def programa_lista(request):
    programas = Programa.objects.all()
    return render(request, 'materias/programa_lista.html', {'programas': programas})


@admin_required
def programa_crear(request):
    if request.method == 'POST':
        form = ProgramaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programa creado exitosamente.')
            return redirect('materias:programa_lista')
    else:
        form = ProgramaForm()
    return render(request, 'materias/programa_form.html', {
        'form': form, 'titulo': 'Registrar Programa', 'accion': 'Guardar'
    })


@admin_required
def programa_editar(request, pk):
    programa = get_object_or_404(Programa, pk=pk)
    if request.method == 'POST':
        form = ProgramaForm(request.POST, instance=programa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Programa actualizado exitosamente.')
            return redirect('materias:programa_lista')
    else:
        form = ProgramaForm(instance=programa)
    return render(request, 'materias/programa_form.html', {
        'form': form, 'titulo': 'Editar Programa', 'accion': 'Actualizar'
    })
