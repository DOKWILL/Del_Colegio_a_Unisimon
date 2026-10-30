"""
Vistas del módulo de Reportes (Módulo 8).

Permite seleccionar una asignación y generar reportes en PDF o Excel
con notas, asistencia y estadísticas del curso.
"""
import io
import pandas as pd
from django.db.models import Exists, OuterRef
from apps.asignaciones.models import Matricula
from django.db.models import F
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
from django.http import HttpResponse


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

@login_required_custom
def descargar_consolidado_asistencias(request):
    """Descargar consolidado general de todas las asistencias en Excel."""
    
    if not request.user.es_admin:
         return HttpResponse('No autorizado', status=403)

    # Subconsulta: Busca si existe una matrícula activa que coincida exactamente 
    # con el estudiante y la asignación de la fila de Asistencia actual.
    matricula_activa_subquery = Matricula.objects.filter(
        estudiante=OuterRef('estudiante_id'),
        asignacion=OuterRef('asignacion_id'),
        activa=True
    )

    # Filtro principal usando Exists
    asistencias = Asistencia.objects.filter(
        estudiante__activo=True
    ).annotate(
        tiene_matricula=Exists(matricula_activa_subquery)
    ).filter(
        tiene_matricula=True # 👈 Solo mantiene a los que pasaron la validación de la subconsulta
    ).select_related(
        'estudiante', 
        'estudiante__colegio',
        'estudiante__programa',
        'asignacion__materia'
    ).order_by('-fecha', 'estudiante__nombre_apellido')

    # Estructurar los datos
    datos = []
    for r in asistencias:
        datos.append({
            'Nombre del Estudiante': r.estudiante.nombre_apellido,
            'Identificación': r.estudiante.identificacion,
            'Fecha de Asistencia': r.fecha.strftime('%d/%m/%Y') if r.fecha else '',
            'Colegio': r.estudiante.colegio.nombre if r.estudiante.colegio else 'N/A',
            'Programa': r.estudiante.programa.nombre if r.estudiante.programa else 'N/A',
            'Materia': r.asignacion.materia.nombre,
            'Estado': r.get_estado_display() 
        })

    # Convertir a DataFrame y guardar
    df = pd.DataFrame(datos)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False, engine='openpyxl')
    content = buffer.getvalue()

    filename = "Consolidado_General_Asistencias.xlsx"
    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response['Content-Length'] = len(content)
    
    return response


@login_required_custom
def descargar_consolidado_notas(request):
    """Descargar consolidado general de todas las notas en Excel."""
    
    if not request.user.es_admin:
         return HttpResponse('No autorizado', status=403)

    # 1. Subconsulta: Validamos que el estudiante siga matriculado activamente en el curso
    matricula_activa = Matricula.objects.filter(
        estudiante=OuterRef('estudiante_id'),
        asignacion=OuterRef('asignacion_id'),
        activa=True
    )

    # 2. Consultar las notas y traer las tablas relacionadas (Programa, Materia, Profesor)
    notas_globales = Nota.objects.filter(
        estudiante__activo=True
    ).annotate(
        tiene_matricula=Exists(matricula_activa)
    ).filter(
        tiene_matricula=True
    ).select_related(
        'estudiante', 
        'estudiante__programa',
        'asignacion__materia',
        'asignacion__profesor'
    ).order_by('asignacion__materia__nombre', 'estudiante__nombre_apellido')

    # 3. Estructurar los datos agregando el Programa y el Curso
    datos = []
    for n in notas_globales:
        datos.append({
            'Identificación': n.estudiante.identificacion,
            'Estudiante': n.estudiante.nombre_apellido,
            'Programa': n.estudiante.programa.nombre if n.estudiante.programa else 'N/A',
            'Curso / Materia': n.asignacion.materia.nombre,
            'Profesor': n.asignacion.profesor.nombres,
            'Parcial 1 (30%)': float(n.parcial1) if n.parcial1 is not None else 0.0,
            'Parcial 2 (30%)': float(n.parcial2) if n.parcial2 is not None else 0.0,
            'Parcial 3 (40%)': float(n.parcial3) if n.parcial3 is not None else 0.0,
            'Definitiva': float(n.definitiva) if n.definitiva is not None else 0.0,
            'Estado': n.estado if n.estado else 'Sin Calificar'
        })

    # 4. Crear DataFrame y dar formato a las columnas en Excel
    df = pd.DataFrame(datos)
    buffer = io.BytesIO()
    
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Consolidado Notas')
        worksheet = writer.sheets['Consolidado Notas']
        
        # Ajustar anchos para una presentación profesional
        worksheet.column_dimensions['A'].width = 15  # ID
        worksheet.column_dimensions['B'].width = 40  # Estudiante
        worksheet.column_dimensions['C'].width = 35  # Programa
        worksheet.column_dimensions['D'].width = 35  # Curso
        worksheet.column_dimensions['E'].width = 30  # Profesor
        worksheet.column_dimensions['F'].width = 15  # Parcial 1
        worksheet.column_dimensions['G'].width = 15  # Parcial 2
        worksheet.column_dimensions['H'].width = 15  # Parcial 3
        worksheet.column_dimensions['I'].width = 15  # Definitiva
        worksheet.column_dimensions['J'].width = 15  # Estado

    content = buffer.getvalue()
    filename = "Consolidado_Global_Notas.xlsx"
    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response
