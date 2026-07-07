"""
Generador de reportes PDF profesional con ReportLab.

Genera reportes académicos con:
- Logo institucional de la universidad
- Encabezado con datos de la materia/programa
- Tabla de notas, asistencia y certificación
- Resumen estadístico al final
"""
import io
import os
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from django.conf import settings


def generar_reporte_pdf(asignacion, notas_data, asistencia_data, buffer=None):
    """
    Genera un reporte PDF profesional para una asignación.

    Args:
        asignacion: Objeto Asignacion con profesor, materia, programa
        notas_data: Lista de dicts con datos de cada estudiante
        asistencia_data: Dict con estadísticas de asistencia
        buffer: BytesIO buffer (se crea uno si no se proporciona)

    Returns:
        BytesIO buffer con el PDF generado
    """
    if buffer is None:
        buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        rightMargin=1 * cm,
        leftMargin=1 * cm,
        topMargin=1 * cm,
        bottomMargin=1 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#09843B'),
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#23987E'),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=3,
    )

    # === LOGO INSTITUCIONAL ===
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'escudo_unisimon.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2 * inch, height=1.2 * inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 5))

    # === ENCABEZADO ===
    elements.append(Paragraph('UNIVERSIDAD SIMÓN BOLÍVAR', title_style))
    elements.append(Paragraph('DEL COLEGIO A UNISIMÓN', subtitle_style))
    elements.append(Paragraph('Reporte de Calificaciones, Asistencia y Certificación', ParagraphStyle(
        'SubInfo', parent=styles['Normal'], fontSize=10, alignment=TA_CENTER,
        textColor=colors.HexColor('#666666'), spaceAfter=12
    )))

    # === INFORMACIÓN DE LA MATERIA ===
    info_data = [
        [Paragraph(f'<b>Programa:</b> {asignacion.programa.nombre}', info_style),
         Paragraph(f'<b>Periodo:</b> {asignacion.periodo}', info_style)],
        [Paragraph(f'<b>Materia:</b> {asignacion.materia.nombre}', info_style),
         Paragraph(f'<b>Código:</b> {asignacion.materia.codigo}', info_style)],
        [Paragraph(f'<b>Profesor:</b> {asignacion.profesor.nombres}', info_style),
         Paragraph(f'<b>Fecha:</b> {date.today().strftime("%d/%m/%Y")}', info_style)],
    ]
    info_table = Table(info_data, colWidths=[doc.width / 2] * 2)
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10))

    # === TABLA DE CALIFICACIONES ===
    cert_style = ParagraphStyle('CertCell', parent=styles['Normal'], fontSize=7, alignment=TA_CENTER)

    header = ['#', 'Identificación', 'Estudiante', 'P1\n(30%)',
              'P2\n(30%)', 'P3\n(40%)', 'Def.',
              '% Asist.', 'Estado', 'Certificación']
    table_data = [header]

    for i, dato in enumerate(notas_data, 1):
        cert_text = dato.get('certificacion', '')
        if cert_text:
            cert_para = Paragraph(f'<b>{cert_text}</b>', cert_style)
        else:
            cert_para = '-'

        fila = [
            str(i),
            str(dato['identificacion']),
            dato['nombre'],
            f"{dato['parcial1']:.1f}" if dato['parcial1'] is not None else '-',
            f"{dato['parcial2']:.1f}" if dato['parcial2'] is not None else '-',
            f"{dato['parcial3']:.1f}" if dato['parcial3'] is not None else '-',
            f"{dato['definitiva']:.2f}" if dato['definitiva'] is not None else '-',
            f"{dato['asistencia_pct']:.1f}%{'*' if dato.get('aplica_nivelacion') else ''}",
            dato['estado'] or '-',
            cert_para,
        ]
        table_data.append(fila)

    col_widths = [0.35*inch, 1.0*inch, 2.0*inch, 0.55*inch, 0.55*inch,
                  0.55*inch, 0.55*inch, 0.7*inch, 0.8*inch, 1.6*inch]

    tabla = Table(table_data, colWidths=col_widths, repeatRows=1)
    tabla.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#09843B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 7),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        # Body
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (8, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        # Borders
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor('#09843B')),
        # Alternating rows
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        # Padding
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))

    # Colorear estado y certificación
    for i, dato in enumerate(notas_data, 1):
        if dato['estado'] == 'Reprobado':
            tabla.setStyle(TableStyle([
                ('TEXTCOLOR', (8, i), (8, i), colors.HexColor('#dc3545')),
                ('FONTNAME', (8, i), (8, i), 'Helvetica-Bold'),
            ]))
        elif dato['estado'] == 'Aprobado':
            tabla.setStyle(TableStyle([
                ('TEXTCOLOR', (8, i), (8, i), colors.HexColor('#28a745')),
                ('FONTNAME', (8, i), (8, i), 'Helvetica-Bold'),
            ]))

        cert = dato.get('certificacion', '')
        if cert == 'Certificable y Homologable':
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (9, i), (9, i), colors.HexColor('#d4edda')),
                ('TEXTCOLOR', (9, i), (9, i), colors.HexColor('#155724')),
            ]))
        elif cert == 'Certificable':
            tabla.setStyle(TableStyle([
                ('BACKGROUND', (9, i), (9, i), colors.HexColor('#d1ecf1')),
                ('TEXTCOLOR', (9, i), (9, i), colors.HexColor('#0c5460')),
            ]))

    elements.append(tabla)
    elements.append(Spacer(1, 8))

    # === LEYENDA DE NIVELACIÓN ===
    elements.append(Paragraph(
        '<b>*</b> Porcentaje ajustado por encuentro de nivelación &nbsp;&nbsp;|&nbsp;&nbsp; '
        '7 encuentros regulares + 1 nivelación',
        ParagraphStyle('Leyenda', parent=styles['Normal'], fontSize=7,
                       textColor=colors.HexColor('#666666'))
    ))
    elements.append(Spacer(1, 12))

    # === RESUMEN ESTADÍSTICO ===
    elements.append(Paragraph('<b>Resumen del Curso</b>', ParagraphStyle(
        'ResumenTitle', parent=styles['Heading3'], fontSize=11,
        textColor=colors.HexColor('#09843B'), spaceAfter=6
    )))

    resumen_data = [
        ['Cantidad de estudiantes:', str(asistencia_data.get('total_estudiantes', 0)),
         'Promedio del curso:', f"{asistencia_data.get('promedio_curso', 0):.2f}"],
        ['Aprobados:', str(asistencia_data.get('aprobados', 0)),
         'Reprobados:', str(asistencia_data.get('reprobados', 0))],
        ['Promedio de asistencia:', f"{asistencia_data.get('promedio_asistencia', 0):.1f}%",
         '', ''],
    ]
    resumen_table = Table(resumen_data, colWidths=[2*inch, 1.5*inch, 2*inch, 1.5*inch])
    resumen_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f0f4f8')),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#09843B')),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#ddd')),
    ]))
    elements.append(resumen_table)

    # === PIE DE PÁGINA ===
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        'Universidad Simón Bolívar — Ing. Wilson Castellanos — © 2026 Todos los derechos reservados.',
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8,
                       alignment=TA_CENTER, textColor=colors.HexColor('#999999'))
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
