"""Vistas del módulo de Espacios Físicos (Módulo 4)."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Sede, Aula
from .forms import SedeForm, AulaForm
from apps.auth_app.decorators import admin_required


@admin_required
def sede_lista(request):
    sedes = Sede.objects.prefetch_related('aulas').all()
    return render(request, 'espacios/sede_lista.html', {'sedes': sedes})


@admin_required
def sede_crear(request):
    if request.method == 'POST':
        form = SedeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sede creada exitosamente.')
            return redirect('espacios:sede_lista')
    else:
        form = SedeForm()
    return render(request, 'espacios/sede_form.html', {
        'form': form, 'titulo': 'Registrar Sede', 'accion': 'Guardar'
    })


@admin_required
def sede_editar(request, pk):
    sede = get_object_or_404(Sede, pk=pk)
    if request.method == 'POST':
        form = SedeForm(request.POST, instance=sede)
        if form.is_valid():
            form.save()
            messages.success(request, 'Sede actualizada exitosamente.')
            return redirect('espacios:sede_lista')
    else:
        form = SedeForm(instance=sede)
    return render(request, 'espacios/sede_form.html', {
        'form': form, 'titulo': 'Editar Sede', 'accion': 'Actualizar'
    })


@admin_required
def aula_lista(request):
    aulas = Aula.objects.select_related('sede').all()
    return render(request, 'espacios/aula_lista.html', {'aulas': aulas})


@admin_required
def aula_crear(request):
    if request.method == 'POST':
        form = AulaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aula creada exitosamente.')
            return redirect('espacios:aula_lista')
    else:
        form = AulaForm()
    return render(request, 'espacios/aula_form.html', {
        'form': form, 'titulo': 'Registrar Aula', 'accion': 'Guardar'
    })


@admin_required
def aula_editar(request, pk):
    aula = get_object_or_404(Aula, pk=pk)
    if request.method == 'POST':
        form = AulaForm(request.POST, instance=aula)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aula actualizada exitosamente.')
            return redirect('espacios:aula_lista')
    else:
        form = AulaForm(instance=aula)
    return render(request, 'espacios/aula_form.html', {
        'form': form, 'titulo': 'Editar Aula', 'accion': 'Actualizar'
    })
