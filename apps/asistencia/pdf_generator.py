import io
import os
from datetime import date
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
from django.conf import settings

def generar_pdf_encuentro(asignacion, encuentro, registros, buffer=None):
    if buffer is None:
        buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(letter),
        rightMargin=1 * cm, leftMargin=1 * cm,
        topMargin=1 * cm, bottomMargin=1 * cm,
    )
    styles = getSampleStyleSheet()
    elements = []

    # Estilos personalizados (basados en tu plantilla)
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=16, textColor=colors.HexColor('#09843B'), alignment=TA_CENTER, spaceAfter=4)
    subtitle_style = ParagraphStyle('CustomSubtitle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor('#23987E'), alignment=TA_CENTER, spaceAfter=10)
    info_style = ParagraphStyle('InfoStyle', parent=styles['Normal'], fontSize=9, spaceAfter=3)

    # Logo Institucional
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'escudo_unisimon.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=1.2 * inch, height=1.2 * inch)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 5))

    # Encabezado
    elements.append(Paragraph('UNIVERSIDAD SIMÓN BOLÍVAR', title_style))
    elements.append(Paragraph(f'Reporte Oficial de Asistencia - Encuentro {encuentro}', subtitle_style))
    
    # Información de la Materia
    info_data = [
        [Paragraph(f'<b>Programa:</b> {asignacion.programa.nombre}', info_style),
         Paragraph(f'<b>Periodo:</b> {asignacion.periodo}', info_style)],
        [Paragraph(f'<b>Materia:</b> {asignacion.materia.nombre} ({asignacion.materia.codigo})', info_style),
         Paragraph(f'<b>Fecha de Emisión:</b> {date.today().strftime("%d/%m/%Y")}', info_style)],
        [Paragraph(f'<b>Profesor:</b> {asignacion.profesor.nombres}', info_style),
         Paragraph('', info_style)],
    ]
    info_table = Table(info_data, colWidths=[doc.width / 2] * 2)
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 15))

    # Estructura de la Tabla
    header = ['#', 'Identificación', 'Estudiante', 'Estado', 'Fecha Asist.', 'Observaciones']
    table_data = [header]

    for i, r in enumerate(registros, 1):
        fecha_str = r.fecha.strftime('%d/%m/%Y') if r.fecha else '-'
        table_data.append([
            str(i), 
            str(r.estudiante.identificacion), 
            r.estudiante.nombre_apellido,
            r.get_estado_display(), 
            fecha_str, 
            r.observaciones or '-'
        ])

    col_widths = [0.4*inch, 1.2*inch, 2.5*inch, 1.0*inch, 1.2*inch, 3.0*inch]
    tabla = Table(table_data, colWidths=col_widths, repeatRows=1)
    
    # Estilos de la tabla
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#09843B')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (4, -1), 'CENTER'),
        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    
    # Colorear dinámicamente los estados de asistencia
    for i, r in enumerate(registros, 1):
        estado = r.get_estado_display()
        if estado == 'Ausente':
            tabla.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#dc3545')), ('FONTNAME', (3, i), (3, i), 'Helvetica-Bold')]))
        elif estado == 'Presente':
            tabla.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#28a745')), ('FONTNAME', (3, i), (3, i), 'Helvetica-Bold')]))
        elif estado == 'Excusa':
            tabla.setStyle(TableStyle([('TEXTCOLOR', (3, i), (3, i), colors.HexColor('#ffc107')), ('FONTNAME', (3, i), (3, i), 'Helvetica-Bold')]))

    elements.append(tabla)
    elements.append(Spacer(1, 30))
    
    # Pie de Página
    elements.append(Paragraph(
        'Universidad Simón Bolívar — Ing. Wilson Castellanos — © 2026 Todos los derechos reservados.',
        ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, alignment=TA_CENTER, textColor=colors.HexColor('#999999'))
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer
