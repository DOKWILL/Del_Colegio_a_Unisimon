"""
Vistas del módulo de Asistencia (Módulo 6).

El profesor selecciona materia → fecha → encuentro y registra la asistencia
de cada estudiante matriculado. El sistema calcula automáticamente
el porcentaje de asistencia, incluyendo el encuentro de nivelación.

Reglas de nivelación:
- 8 encuentros totales (7 regulares + 1 nivelación)
- Si el estudiante asistió a los 7 regulares: 100%, nivelación no aplica
- Si faltó a 1 regular y asiste a nivelación: 100%
- Si faltó a 2 regulares y asiste a nivelación: 80%
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from .models import Asistencia
from apps.asignaciones.models import Asignacion, Matricula
from apps.notas.models import Nota
from apps.auth_app.decorators import login_required_custom

# Encuentro de nivelación siempre es el 8
ENCUENTRO_NIVELACION = 8
ENCUENTROS_REGULARES = 7


def calcular_asistencia_con_nivelacion(asignacion, estudiante):
    """
    Calcula la asistencia de un estudiante considerando las reglas de nivelación.

    Returns:
        dict con: presentes_regulares, ausentes_regulares, asistio_nivelacion,
                  porcentaje_final, excusas, total_registros, aplica_nivelacion
    """
    asistencias = Asistencia.objects.filter(
        asignacion=asignacion, estudiante=estudiante
    )

    # Separar encuentros regulares (1-6) y nivelación (7)
    regulares = asistencias.filter(encuentro__lte=ENCUENTROS_REGULARES)
    nivelacion = asistencias.filter(encuentro=ENCUENTRO_NIVELACION)

    total_regulares = regulares.count()
    presentes_regulares = regulares.filter(
        Q(estado='presente') | Q(estado='retardo')
    ).count()
    ausentes_regulares = total_regulares - presentes_regulares
    excusas = regulares.filter(estado='excusa').count()

    # ¿Asistió a la nivelación?
    asistio_nivelacion = nivelacion.filter(
        Q(estado='presente') | Q(estado='retardo')
    ).exists()
    tiene_nivelacion = nivelacion.exists()

    # Calcular faltas en los 7 encuentros regulares
    faltas_regulares = ENCUENTROS_REGULARES - presentes_regulares if total_regulares >= ENCUENTROS_REGULARES else (total_regulares - presentes_regulares if total_regulares > 0 else 0)

    # Determinar porcentaje con reglas de nivelación
    aplica_nivelacion = False
    if total_regulares == 0:
        porcentaje_final = 0
    elif presentes_regulares >= ENCUENTROS_REGULARES:
        # 100% asistencia regular, nivelación no cuenta
        porcentaje_final = 100.0
    elif faltas_regulares == 1 and asistio_nivelacion:
        # Faltó a 1, asistió a nivelación → 100%
        porcentaje_final = 100.0
        aplica_nivelacion = True
    elif faltas_regulares == 2 and asistio_nivelacion:
        # Faltó a 2, asistió a nivelación → 80%
        porcentaje_final = 80.0
        aplica_nivelacion = True
    else:
        # Cálculo estándar (sin beneficio de nivelación)
        porcentaje_final = round(presentes_regulares / total_regulares * 100, 1) if total_regulares > 0 else 0

    return {
        'presentes_regulares': presentes_regulares,
        'ausentes_regulares': ausentes_regulares,
        'excusas': excusas,
        'total_registros': total_regulares + (1 if tiene_nivelacion else 0),
        'asistio_nivelacion': asistio_nivelacion,
        'tiene_nivelacion': tiene_nivelacion,
        'aplica_nivelacion': aplica_nivelacion,
        'faltas_regulares': faltas_regulares,
        'porcentaje_final': porcentaje_final,
    }


def calcular_certificacion(porcentaje_final, definitiva):
    """
    Determina la certificación del estudiante.

    - "Certificable y Homologable": 100% asistencia + promedio >= 4.0
    - "Certificable": >= 80% asistencia + promedio >= 4.0
    - "": No aplica
    """
    if definitiva is None:
        return ''
    if porcentaje_final >= 100 and definitiva >= 4.0:
        return 'Certificable y Homologable'
    elif porcentaje_final >= 80 and definitiva >= 4.0:
        return 'Certificable'
    return ''


@login_required_custom
def seleccionar_materia(request):
    """Paso 1: El profesor selecciona la materia para tomar asistencia."""
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

    return render(request, 'asistencia/seleccionar_materia.html', {
        'asignaciones': asignaciones
    })


@login_required_custom
def registrar_asistencia(request, asignacion_id):
    """Paso 2: Registrar asistencia para una asignación específica."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    # Verificar que el profesor solo acceda a sus asignaciones
    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        messages.error(request, 'No tiene permisos para acceder a esta asignación.')
        return redirect('asistencia:seleccionar_materia')

    # Obtener estudiantes matriculados
    matriculas = Matricula.objects.filter(
        asignacion=asignacion, activa=True
    ).select_related('estudiante').order_by('estudiante__nombre_apellido')

    # Calcular el próximo número de encuentro
    ultimo_encuentro = Asistencia.objects.filter(
        asignacion=asignacion
    ).values_list('encuentro', flat=True).distinct().order_by('-encuentro').first()
    proximo_encuentro = (ultimo_encuentro or 0) + 1

    # Si ya completaron los 6 regulares, sugerir nivelación
    es_nivelacion = proximo_encuentro == ENCUENTRO_NIVELACION

    fecha_hoy = timezone.localdate()

    if request.method == 'POST':
        fecha = request.POST.get('fecha', str(fecha_hoy))
        encuentro = int(request.POST.get('encuentro', proximo_encuentro))
        observaciones_general = request.POST.get('observaciones', '')

        registros_creados = 0
        for matricula in matriculas:
            estado = request.POST.get(f'estado_{matricula.estudiante.id}', 'presente')
            obs = request.POST.get(f'obs_{matricula.estudiante.id}', observaciones_general)

            Asistencia.objects.update_or_create(
                asignacion=asignacion,
                estudiante=matricula.estudiante,
                encuentro=encuentro,
                defaults={
                    'fecha': fecha,
                    'estado': estado,
                    'observaciones': obs,
                }
            )
            registros_creados += 1

        tipo = 'de nivelación' if encuentro == ENCUENTRO_NIVELACION else f'{encuentro}'
        messages.success(
            request,
            f'Asistencia del encuentro {tipo} registrada para {registros_creados} estudiante(s).'
        )
        return redirect('asistencia:ver_asistencia', asignacion_id=asignacion.id)

    return render(request, 'asistencia/registrar_asistencia.html', {
        'asignacion': asignacion,
        'matriculas': matriculas,
        'fecha_hoy': fecha_hoy,
        'proximo_encuentro': proximo_encuentro,
        'es_nivelacion': es_nivelacion,
        'ENCUENTRO_NIVELACION': ENCUENTRO_NIVELACION,
    })


@login_required_custom
def ver_asistencia(request, asignacion_id):
    """Ver resumen de asistencia de una asignación con nivelación."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'),
        pk=asignacion_id
    )

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        messages.error(request, 'No tiene permisos para acceder a esta asignación.')
        return redirect('asistencia:seleccionar_materia')

    # Obtener estudiantes matriculados
    matriculas = Matricula.objects.filter(
        asignacion=asignacion, activa=True
    ).select_related('estudiante')

    # Total de encuentros registrados
    total_encuentros = Asistencia.objects.filter(
        asignacion=asignacion
    ).values('encuentro').distinct().count()

    # Verificar si hay nivelación
    hay_nivelacion = Asistencia.objects.filter(
        asignacion=asignacion, encuentro=ENCUENTRO_NIVELACION
    ).exists()

    # Calcular estadísticas por estudiante
    resumen = []
    for matricula in matriculas:
        datos = calcular_asistencia_con_nivelacion(asignacion, matricula.estudiante)

        # Obtener nota para certificación
        try:
            nota = Nota.objects.get(asignacion=asignacion, estudiante=matricula.estudiante)
            definitiva = nota.definitiva
        except Nota.DoesNotExist:
            definitiva = None

        certificacion = calcular_certificacion(datos['porcentaje_final'], definitiva)

        resumen.append({
            'estudiante': matricula.estudiante,
            'total': datos['total_registros'],
            'presentes': datos['presentes_regulares'],
            'ausentes': datos['ausentes_regulares'],
            'excusas': datos['excusas'],
            'porcentaje': datos['porcentaje_final'],
            'asistio_nivelacion': datos['asistio_nivelacion'],
            'aplica_nivelacion': datos['aplica_nivelacion'],
            'certificacion': certificacion,
            'definitiva': definitiva,
        })

    # Encuentros registrados (para listar)
    encuentros = Asistencia.objects.filter(
        asignacion=asignacion
    ).values('encuentro', 'fecha').distinct().order_by('encuentro')

    return render(request, 'asistencia/ver_asistencia.html', {
        'asignacion': asignacion,
        'resumen': resumen,
        'total_encuentros': total_encuentros,
        'encuentros': encuentros,
        'hay_nivelacion': hay_nivelacion,
        'ENCUENTRO_NIVELACION': ENCUENTRO_NIVELACION,
    })


@login_required_custom
def detalle_encuentro(request, asignacion_id, encuentro):
    """Ver detalle de asistencia de un encuentro específico y permitir su edición."""
    asignacion = get_object_or_404(Asignacion, pk=asignacion_id)

    if request.user.es_profesor and request.user.profesor != asignacion.profesor:
        messages.error(request, 'No tiene permisos.')
        return redirect('asistencia:seleccionar_materia')

    # Traemos los registros actuales
    registros = Asistencia.objects.filter(
        asignacion=asignacion, encuentro=encuentro
    ).select_related('estudiante').order_by('estudiante__nombre_apellido')

    # Lógica para procesar la edición cuando se envía el formulario
    if request.method == 'POST':
        registros_actualizados = 0
        
        for registro in registros:
            # Capturamos los nuevos valores usando el ID único de cada registro
            nuevo_estado = request.POST.get(f'estado_{registro.id}')
            nueva_fecha = request.POST.get(f'fecha_{registro.id}')
            nuevas_obs = request.POST.get(f'obs_{registro.id}', '')

            # Actualizamos solo si hay datos válidos
            if nuevo_estado and nueva_fecha:
                registro.estado = nuevo_estado
                registro.fecha = nueva_fecha
                registro.observaciones = nuevas_obs
                registro.save()
                registros_actualizados += 1

        messages.success(request, f'Se actualizaron {registros_actualizados} registros del encuentro {encuentro}.')
        return redirect('asistencia:ver_asistencia', asignacion_id=asignacion.id)

    es_nivelacion = encuentro == ENCUENTRO_NIVELACION

    return render(request, 'asistencia/detalle_encuentro.html', {
        'asignacion': asignacion,
        'encuentro': encuentro,
        'registros': registros,
        'es_nivelacion': es_nivelacion,
    })
