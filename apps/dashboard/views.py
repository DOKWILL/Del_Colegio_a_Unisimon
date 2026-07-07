"""
Vista principal del Dashboard.

Muestra KPIs (total estudiantes, profesores, materias, programas,
asistencia promedio, promedio académico) y datos para gráficos Chart.js.
Soporta filtrado interactivo por programa vía AJAX.
"""
import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg, Count, Q
from apps.auth_app.decorators import login_required_custom
from apps.estudiantes.models import Estudiante
from apps.profesores.models import Profesor
from apps.materias.models import Materia, Programa
from apps.asignaciones.models import Asignacion, Matricula
from apps.asistencia.models import Asistencia
from apps.notas.models import Nota


@login_required_custom
def index(request):
    """Dashboard principal con estadísticas y gráficos."""

    if request.user.es_profesor and request.user.profesor:
        # Vista de profesor: solo sus datos
        profesor = request.user.profesor
        asignaciones = Asignacion.objects.filter(
            profesor=profesor, activa=True
        ).select_related('materia', 'programa')

        est_ids = Matricula.objects.filter(
            asignacion__in=asignaciones, activa=True
        ).values_list('estudiante_id', flat=True).distinct()

        total_estudiantes = len(est_ids)
        total_materias = asignaciones.count()
        total_programas = asignaciones.values('programa').distinct().count()

        # Promedio de asistencia de sus estudiantes
        asistencias = Asistencia.objects.filter(asignacion__in=asignaciones)
        total_registros = asistencias.count()
        presentes = asistencias.filter(
            Q(estado='presente') | Q(estado='retardo')
        ).count()
        asistencia_promedio = round(presentes / total_registros * 100, 1) if total_registros > 0 else 0

        # Promedio académico de sus estudiantes
        notas = Nota.objects.filter(asignacion__in=asignaciones, definitiva__isnull=False)
        promedio_academico = notas.aggregate(avg=Avg('definitiva'))['avg'] or 0
        promedio_academico = round(promedio_academico, 2)

        # Datos para gráficos
        aprobados = notas.filter(estado='Aprobado').count()
        reprobados = notas.filter(estado='Reprobado').count()

        # Asistencia por materia
        asist_por_materia = []
        for asig in asignaciones:
            total_asig = Asistencia.objects.filter(asignacion=asig).count()
            pres_asig = Asistencia.objects.filter(
                asignacion=asig
            ).filter(Q(estado='presente') | Q(estado='retardo')).count()
            pct = round(pres_asig / total_asig * 100, 1) if total_asig > 0 else 0
            asist_por_materia.append({
                'materia': str(asig.materia.nombre),
                'porcentaje': pct
            })

        context = {
            'total_estudiantes': total_estudiantes,
            'total_profesores': 1,
            'total_materias': total_materias,
            'total_programas': total_programas,
            'asistencia_promedio': asistencia_promedio,
            'promedio_academico': promedio_academico,
            'aprobados': aprobados,
            'reprobados': reprobados,
            'asist_por_materia_json': json.dumps(asist_por_materia),
            'es_profesor': True,
        }
    else:
        # Vista de administrador: datos globales
        total_estudiantes = Estudiante.objects.filter(activo=True).count()
        total_profesores = Profesor.objects.filter(activo=True).count()
        total_materias = Materia.objects.filter(activo=True).count()
        total_programas = Programa.objects.filter(activo=True).count()

        # Asistencia promedio global
        total_registros = Asistencia.objects.count()
        presentes = Asistencia.objects.filter(
            Q(estado='presente') | Q(estado='retardo')
        ).count()
        asistencia_promedio = round(presentes / total_registros * 100, 1) if total_registros > 0 else 0

        # Promedio académico global
        promedio_academico = Nota.objects.filter(
            definitiva__isnull=False
        ).aggregate(avg=Avg('definitiva'))['avg'] or 0
        promedio_academico = round(promedio_academico, 2)

        aprobados = Nota.objects.filter(estado='Aprobado').count()
        reprobados = Nota.objects.filter(estado='Reprobado').count()

        # Estudiantes por programa
        est_por_programa = list(
            Programa.objects.filter(activo=True).annotate(
                total=Count('estudiantes', filter=Q(estudiantes__activo=True))
            ).values('id', 'nombre', 'total')
        )

        # Asistencia por materia (top 10)
        asignaciones = Asignacion.objects.filter(activa=True).select_related('materia', 'programa')[:10]
        asist_por_materia = []
        for asig in asignaciones:
            total_asig = Asistencia.objects.filter(asignacion=asig).count()
            pres_asig = Asistencia.objects.filter(
                asignacion=asig
            ).filter(Q(estado='presente') | Q(estado='retardo')).count()
            pct = round(pres_asig / total_asig * 100, 1) if total_asig > 0 else 0
            asist_por_materia.append({
                'materia': str(asig.materia.nombre)[:25],
                'programa_id': asig.programa_id,
                'porcentaje': pct
            })

        context = {
            'total_estudiantes': total_estudiantes,
            'total_profesores': total_profesores,
            'total_materias': total_materias,
            'total_programas': total_programas,
            'asistencia_promedio': asistencia_promedio,
            'promedio_academico': promedio_academico,
            'aprobados': aprobados,
            'reprobados': reprobados,
            'est_por_programa_json': json.dumps(est_por_programa),
            'asist_por_materia_json': json.dumps(asist_por_materia),
            'es_profesor': False,
        }

    return render(request, 'dashboard/index.html', context)


@login_required_custom
def dashboard_filter(request):
    """API endpoint para filtrado interactivo del dashboard por programa."""
    programa_id = request.GET.get('programa_id')

    if not programa_id:
        return JsonResponse({'error': 'programa_id requerido'}, status=400)

    try:
        programa = Programa.objects.get(pk=programa_id)
    except Programa.DoesNotExist:
        return JsonResponse({'error': 'Programa no encontrado'}, status=404)

    # Estudiantes del programa
    total_estudiantes = Estudiante.objects.filter(
        programa=programa, activo=True
    ).count()

    # Materias del programa (asignaciones activas)
    asignaciones = Asignacion.objects.filter(
        programa=programa, activa=True
    ).select_related('materia')
    total_materias = asignaciones.values('materia').distinct().count()

    # Profesores del programa
    total_profesores = asignaciones.values('profesor').distinct().count()

    # Asistencia
    asistencias = Asistencia.objects.filter(asignacion__in=asignaciones)
    total_reg = asistencias.count()
    presentes = asistencias.filter(
        Q(estado='presente') | Q(estado='retardo')
    ).count()
    asistencia_promedio = round(presentes / total_reg * 100, 1) if total_reg > 0 else 0

    # Notas
    notas = Nota.objects.filter(asignacion__in=asignaciones, definitiva__isnull=False)
    promedio_academico = notas.aggregate(avg=Avg('definitiva'))['avg'] or 0
    promedio_academico = round(promedio_academico, 2)
    aprobados = notas.filter(estado='Aprobado').count()
    reprobados = notas.filter(estado='Reprobado').count()

    # Asistencia por materia
    asist_por_materia = []
    for asig in asignaciones:
        total_asig = Asistencia.objects.filter(asignacion=asig).count()
        pres_asig = Asistencia.objects.filter(
            asignacion=asig
        ).filter(Q(estado='presente') | Q(estado='retardo')).count()
        pct = round(pres_asig / total_asig * 100, 1) if total_asig > 0 else 0
        asist_por_materia.append({
            'materia': str(asig.materia.nombre)[:25],
            'porcentaje': pct
        })

    return JsonResponse({
        'programa_nombre': programa.nombre,
        'total_estudiantes': total_estudiantes,
        'total_profesores': total_profesores,
        'total_materias': total_materias,
        'total_programas': 1,
        'asistencia_promedio': asistencia_promedio,
        'promedio_academico': promedio_academico,
        'aprobados': aprobados,
        'reprobados': reprobados,
        'asist_por_materia': asist_por_materia,
    })
