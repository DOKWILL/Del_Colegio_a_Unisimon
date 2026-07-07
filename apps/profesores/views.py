"""Vistas del módulo de Profesores (Módulo 2)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Profesor
from .forms import ProfesorForm
from apps.auth_app.decorators import admin_required


@admin_required
def profesor_lista(request):
    query = request.GET.get('q', '')
    profesores = Profesor.objects.all()
    if query:
        profesores = profesores.filter(
            Q(nombres__icontains=query) | Q(identificacion__icontains=query)
        )
    return render(request, 'profesores/profesor_lista.html', {
        'profesores': profesores, 'query': query
    })


@admin_required
def profesor_crear(request):
    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profesor creado exitosamente.')
            return redirect('profesores:lista')
    else:
        form = ProfesorForm()
    return render(request, 'profesores/profesor_form.html', {
        'form': form, 'titulo': 'Registrar Profesor', 'accion': 'Guardar'
    })


@admin_required
def profesor_editar(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        form = ProfesorForm(request.POST, instance=profesor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profesor actualizado exitosamente.')
            return redirect('profesores:lista')
    else:
        form = ProfesorForm(instance=profesor)
    return render(request, 'profesores/profesor_form.html', {
        'form': form, 'titulo': 'Editar Profesor', 'accion': 'Actualizar'
    })


@admin_required
def profesor_eliminar(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == 'POST':
        profesor.delete()
        messages.success(request, 'Profesor eliminado exitosamente.')
        return redirect('profesores:lista')
    return render(request, 'profesores/profesor_confirmar_eliminar.html', {
        'profesor': profesor
    })
