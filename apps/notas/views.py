"""
Vistas del módulo de Calificaciones (Módulo 7).

El profesor registra parcial 1, 2 y 3 para cada estudiante.
La definitiva y el estado se calculan automáticamente en el modelo.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef # <-- Agregado Exists, OuterRef

from .models import Nota
from apps.asignaciones.models import Asignacion, Matricula
from apps.auth_app.decorators import login_required_custom


@login_required_custom
def registrar_notas(request, asignacion_id):
    """Registrar notas para los estudiantes de una asignación."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        messages.error(request, 'No tiene permisos para acceder a esta asignación.')
        return redirect('notas:seleccionar_materia')

    # Obtener estudiantes matriculados
    matriculas = Matricula.objects.filter(
        asignacion=asignacion, activa=True
    ).select_related('estudiante').order_by('estudiante__nombre_apellido')

    # Crear registros de notas si no existen
    for matricula in matriculas:
        Nota.objects.get_or_create(
            asignacion=asignacion,
            estudiante=matricula.estudiante
        )

    if request.method == 'POST':
        for matricula in matriculas:
            est_id = matricula.estudiante.id
            try:
                nota = Nota.objects.get(
                    asignacion=asignacion,
                    estudiante=matricula.estudiante
                )
                
                # Usamos request.POST.get sin fallback vacío. 
                p1 = request.POST.get(f'parcial1_{est_id}')
                p2 = request.POST.get(f'parcial2_{est_id}')
                p3 = request.POST.get(f'parcial3_{est_id}')

                # Solo se actualiza si el dato viene en el POST
                if p1 is not None:
                    nota.parcial1 = float(p1) if p1.strip() else None
                if p2 is not None:
                    nota.parcial2 = float(p2) if p2.strip() else None
                if p3 is not None:
                    nota.parcial3 = float(p3) if p3.strip() else None
                    
                nota.save()  # calcular_definitiva() es llamado en save()
            except (ValueError, Nota.DoesNotExist):
                continue

        messages.success(request, 'Calificaciones guardadas exitosamente.')
        return redirect('notas:registrar', asignacion_id=asignacion.id)

    # === SOLUCIÓN APLICADA ===
    # Subconsulta para verificar si el estudiante tiene una matrícula activa en esta asignación
    matricula_activa = Matricula.objects.filter(
        estudiante=OuterRef('estudiante_id'),
        asignacion=asignacion,
        activa=True
    )

    # Filtrar notas para mostrar SOLAMENTE a los que pasaron la subconsulta
    notas = Nota.objects.filter(
        asignacion=asignacion
    ).annotate(
        tiene_matricula=Exists(matricula_activa)
    ).filter(
        tiene_matricula=True
    ).select_related('estudiante').order_by('estudiante__nombre_apellido')

    return render(request, 'notas/registrar_notas.html', {
        'asignacion': asignacion,
        'notas': notas,
    })


@login_required_custom
def ver_notas(request, asignacion_id):
    """Ver resumen de calificaciones con definitivas y estados."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        messages.error(request, 'No tiene permisos.')
        return redirect('notas:seleccionar_materia')

    # === SOLUCIÓN APLICADA ===
    matricula_activa = Matricula.objects.filter(
        estudiante=OuterRef('estudiante_id'),
        asignacion=asignacion,
        activa=True
    )

    notas = Nota.objects.filter(
        asignacion=asignacion
    ).annotate(
        tiene_matricula=Exists(matricula_activa)
    ).filter(
        tiene_matricula=True
    ).select_related('estudiante').order_by('estudiante__nombre_apellido')

    # Estadísticas
    total = notas.count()
    aprobados = notas.filter(estado='Aprobado').count()
    reprobados = notas.filter(estado='Reprobado').count()
    definitivas = [n.definitiva for n in notas if n.definitiva is not None]
    promedio = round(sum(definitivas) / len(definitivas), 2) if definitivas else 0

    return render(request, 'notas/ver_notas.html', {
        'asignacion': asignacion,
        'notas': notas,
        'total': total,
        'aprobados': aprobados,
        'reprobados': reprobados,
        'promedio': promedio,
    })
