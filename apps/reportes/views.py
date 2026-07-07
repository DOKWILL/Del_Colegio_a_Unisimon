"""
Vistas del módulo de Reportes (Módulo 8).

Permite seleccionar una asignación y generar reportes en PDF o Excel
con notas, asistencia y estadísticas del curso.
"""
import io
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q

from apps.asignaciones.models import Asignacion, Matricula
from apps.notas.models import Nota
from apps.asistencia.models import Asistencia
from apps.auth_app.decorators import login_required_custom
from .pdf_generator import generar_reporte_pdf
from .excel_generator import generar_reporte_excel
from apps.asistencia.views import calcular_asistencia_con_nivelacion, calcular_certificacion


def _get_reporte_data(asignacion):
    """Obtiene los datos necesarios para generar un reporte con nivelación."""
    matriculas = Matricula.objects.filter(
        asignacion=asignacion, activa=True
    ).select_related('estudiante').order_by('estudiante__nombre_apellido')

    total_encuentros = Asistencia.objects.filter(
        asignacion=asignacion
    ).values('encuentro').distinct().count()

    notas_data = []
    total_definitiva = 0
    total_con_nota = 0
    total_asistencia_pct = 0
    aprobados = 0
    reprobados = 0

    for matricula in matriculas:
        estudiante = matricula.estudiante

        # Nota
        try:
            nota = Nota.objects.get(asignacion=asignacion, estudiante=estudiante)
        except Nota.DoesNotExist:
            nota = None

        # Asistencia con lógica de nivelación
        datos_asist = calcular_asistencia_con_nivelacion(asignacion, estudiante)
        pct_asistencia = datos_asist['porcentaje_final']

        # Certificación
        definitiva = nota.definitiva if nota else None
        certificacion = calcular_certificacion(pct_asistencia, definitiva)

        dato = {
            'nombre': estudiante.nombre_apellido,
            'identificacion': estudiante.identificacion,
            'parcial1': nota.parcial1 if nota else None,
            'parcial2': nota.parcial2 if nota else None,
            'parcial3': nota.parcial3 if nota else None,
            'definitiva': definitiva,
            'estado': nota.estado if nota else '',
            'asistencia_pct': pct_asistencia,
            'asistio_nivelacion': datos_asist['asistio_nivelacion'],
            'aplica_nivelacion': datos_asist['aplica_nivelacion'],
            'certificacion': certificacion,
        }
        notas_data.append(dato)

        if nota and nota.definitiva is not None:
            total_definitiva += nota.definitiva
            total_con_nota += 1
            if nota.estado == 'Aprobado':
                aprobados += 1
            elif nota.estado == 'Reprobado':
                reprobados += 1

        total_asistencia_pct += pct_asistencia

    total_estudiantes = len(notas_data)
    promedio_curso = round(total_definitiva / total_con_nota, 2) if total_con_nota > 0 else 0
    promedio_asistencia = round(total_asistencia_pct / total_estudiantes, 1) if total_estudiantes > 0 else 0

    asistencia_data = {
        'total_estudiantes': total_estudiantes,
        'aprobados': aprobados,
        'reprobados': reprobados,
        'promedio_curso': promedio_curso,
        'promedio_asistencia': promedio_asistencia,
        'total_encuentros': total_encuentros,
    }

    return notas_data, asistencia_data


@login_required_custom
def seleccionar_materia_reporte(request):
    """Seleccionar materia para generar reporte."""
    if request.user.es_admin:
        asignaciones = Asignacion.objects.filter(activa=True).select_related(
            'profesor', 'materia', 'programa'
        )
    elif request.user.es_profesor and request.user.profesor:
        asignaciones = Asignacion.objects.filter(
            profesor=request.user.profesor, activa=True
        ).select_related('materia', 'programa')
    else:
        asignaciones = Asignacion.objects.none()

    return render(request, 'reportes/seleccionar_materia.html', {
        'asignaciones': asignaciones
    })


@login_required_custom
def vista_previa_reporte(request, asignacion_id):
    """Vista previa del reporte en HTML."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        return HttpResponse('No autorizado', status=403)

    notas_data, asistencia_data = _get_reporte_data(asignacion)

    return render(request, 'reportes/vista_previa.html', {
        'asignacion': asignacion,
        'notas_data': notas_data,
        'stats': asistencia_data,
    })


@login_required_custom
def descargar_pdf(request, asignacion_id):
    """Descargar reporte en PDF."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        return HttpResponse('No autorizado', status=403)

    notas_data, asistencia_data = _get_reporte_data(asignacion)

    buffer = io.BytesIO()
    generar_reporte_pdf(asignacion, notas_data, asistencia_data, buffer)

    content = buffer.getvalue()
    filename = f"reporte_{asignacion.materia.codigo}_{asignacion.periodo}.pdf"
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(content)
    return response


@login_required_custom
def descargar_excel(request, asignacion_id):
    """Descargar reporte en Excel."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        return HttpResponse('No autorizado', status=403)

    notas_data, asistencia_data = _get_reporte_data(asignacion)

    buffer = io.BytesIO()
    generar_reporte_excel(asignacion, notas_data, asistencia_data, buffer)

    content = buffer.getvalue()
    filename = f"reporte_{asignacion.materia.codigo}_{asignacion.periodo}.xlsx"
    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(content)
    return response
