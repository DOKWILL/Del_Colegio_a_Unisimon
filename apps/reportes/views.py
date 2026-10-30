"""
Vistas del módulo de Reportes (Módulo 8).

Permite seleccionar una asignación y generar reportes en PDF o Excel
con notas, asistencia y estadísticas del curso.
"""
import io
import pandas as pd
from django.utils import timezone
from django.db.models import Exists, OuterRef, F, Q
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

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
    """Descargar consolidado general de notas con el formato oficial e institucional."""
    if not request.user.es_admin:
         return HttpResponse('No autorizado', status=403)

    # 1. Subconsulta para asegurar que solo aparezcan estudiantes con matrícula activa
    matricula_activa = Matricula.objects.filter(
        estudiante=OuterRef('estudiante_id'),
        asignacion=OuterRef('asignacion_id'),
        activa=True
    )

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

    # 2. Construcción NATIVA del documento de Excel
    wb = Workbook()
    ws = wb.active
    ws.title = "Consolidado Notas Global"

    # Definir la paleta de colores y estilos (Igual al reporte individual)
    green_fill = PatternFill(start_color="0009843B", end_color="0009843B", fill_type="solid")
    white_font = Font(color="FFFFFF", bold=True)
    bold_font = Font(bold=True)
    center_aligned = Alignment(horizontal="center", vertical="center")
    left_aligned = Alignment(horizontal="left", vertical="center")
    border = Border(
        left=Side(style='thin', color="DDDDDD"), 
        right=Side(style='thin', color="DDDDDD"), 
        top=Side(style='thin', color="DDDDDD"), 
        bottom=Side(style='thin', color="DDDDDD")
    )

    # 3. Encabezados Institucionales Superiores
    ws.merge_cells('A1:L1')
    ws['A1'] = "UNIVERSIDAD SIMÓN BOLÍVAR"
    ws['A1'].font = Font(bold=True, size=12)

    ws.merge_cells('A2:L2')
    ws['A2'] = "DEL COLEGIO A UNISIMÓN — Consolidado Global de Calificaciones, Asistencia y Certificación"
    ws['A2'].font = Font(bold=True, size=11)

    ws['A4'] = "Fecha de Generación:"
    ws['A4'].font = bold_font
    ws['B4'] = timezone.localdate().strftime('%d/%m/%Y')

    # 4. Títulos de la Tabla (Agregando Programa y Curso)
    encabezados = [
        '#', 'Identificación', 'Estudiante', 'Programa', 'Materia / Curso',
        'Parcial 1 (30%)', 'Parcial 2 (30%)', 'Parcial 3 (40%)',
        'Definitiva', '% Asistencia', 'Estado', 'Certificación'
    ]
    
    # Imprimir barra verde de encabezados en la fila 6
    row_num = 6
    for col_num, titulo in enumerate(encabezados, 1):
        cell = ws.cell(row=row_num, column=col_num)
        cell.value = titulo
        cell.fill = green_fill
        cell.font = white_font
        cell.alignment = center_aligned
        cell.border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))

    # 5. Iterar e inyectar Datos
    for idx, n in enumerate(notas_globales, 1):
        row_num += 1
        
        # Inyectar la lógica del módulo de asistencia para calcular porcentajes exactos
        datos_asistencia = calcular_asistencia_con_nivelacion(n.asignacion, n.estudiante)
        porcentaje_asist = datos_asistencia['porcentaje_final']
        certificacion = calcular_certificacion(porcentaje_asist, n.definitiva)

        def format_nota(val):
            return float(val) if val is not None else '-'

        datos_fila = [
            idx,
            n.estudiante.identificacion,
            n.estudiante.nombre_apellido,
            n.estudiante.programa.nombre if n.estudiante.programa else 'N/A',
            n.asignacion.materia.nombre,
            format_nota(n.parcial1),
            format_nota(n.parcial2),
            format_nota(n.parcial3),
            format_nota(n.definitiva),
            f"{porcentaje_asist}%",
            n.estado if n.estado else '-',
            certificacion if certificacion else '-'
        ]
        
        for col_num, valor in enumerate(datos_fila, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = valor
            cell.border = border
            
            # Formatear celdas numéricas y de estados para alineación
            if col_num in [1, 6, 7, 8, 9, 10, 11, 12]:
                cell.alignment = center_aligned
            else:
                cell.alignment = left_aligned
                
            # Aplicar formato de un decimal "0.0" estrictamente a las notas
            if col_num in [6, 7, 8, 9] and valor != '-':
                cell.number_format = '0.0'

    # 6. Ajustar visualmente los anchos de columna
    anchos = {
        'A': 5, 'B': 15, 'C': 40, 'D': 35, 'E': 40, 
        'F': 16, 'G': 16, 'H': 16, 'I': 14, 'J': 15, 'K': 16, 'L': 30
    }
    for col_letra, ancho in anchos.items():
        ws.column_dimensions[col_letra].width = ancho

    # Congelar el panel superior para que el encabezado baje con el scroll
    ws.freeze_panes = 'A7'

    buffer = io.BytesIO()
    wb.save(buffer)
    content = buffer.getvalue()
    filename = "Consolidado_Global_Notas.xlsx"
    
    response = HttpResponse(
        content,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
