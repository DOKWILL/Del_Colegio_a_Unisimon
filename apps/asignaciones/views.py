"""Vistas del módulo de Asignación Académica (Módulo 5)."""
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, ProtectedError # 👈 Importación agregada

from .models import Asignacion, Matricula
from .forms import AsignacionForm, MatriculaForm
from apps.profesores.models import Profesor
from apps.auth_app.decorators import login_required_custom, admin_required


def _detectar_cruces(asignaciones):
    """
    Detecta todos los cruces de horario entre las asignaciones activas.
    Un cruce ocurre cuando: A.inicio < B.fin AND A.fin > B.inicio
    Ejemplo: 8:00-10:00 cruza con 9:00-11:00 porque 8<11 y 10>9

    Returns:
        tuple: (cruces_detectados, set_ids_con_cruce)
    """
    cruces = []
    ids_con_cruce = set()
    activas = [a for a in asignaciones if a.activa and a.dia_semana and a.hora_inicio and a.hora_fin]

    for i, a in enumerate(activas):
        for b in activas[i + 1:]:
            if a.periodo != b.periodo or a.dia_semana != b.dia_semana:
                continue

            # Verificar solapamiento temporal: A.inicio < B.fin AND A.fin > B.inicio
            if a.hora_inicio < b.hora_fin and a.hora_fin > b.hora_inicio:
                # Cruce por profesor
                if a.profesor_id == b.profesor_id:
                    cruces.append({
                        'tipo': 'profesor',
                        'profesor': a.profesor.nombres,
                        'materia1': a.materia.nombre,
                        'horario1': f"{a.hora_inicio.strftime('%H:%M')}-{a.hora_fin.strftime('%H:%M')}",
                        'materia2': b.materia.nombre,
                        'horario2': f"{b.hora_inicio.strftime('%H:%M')}-{b.hora_fin.strftime('%H:%M')}",
                        'dia': a.get_dia_semana_display(),
                        'periodo': a.periodo,
                        'aula1': str(a.aula) if a.aula else 'Sin aula',
                        'aula2': str(b.aula) if b.aula else 'Sin aula',
                    })
                    ids_con_cruce.update([a.pk, b.pk])

                # Cruce por aula
                if a.aula_id and a.aula_id == b.aula_id:
                    cruces.append({
                        'tipo': 'aula',
                        'aula': str(a.aula),
                        'materia1': a.materia.nombre,
                        'horario1': f"{a.hora_inicio.strftime('%H:%M')}-{a.hora_fin.strftime('%H:%M')}",
                        'materia2': b.materia.nombre,
                        'horario2': f"{b.hora_inicio.strftime('%H:%M')}-{b.hora_fin.strftime('%H:%M')}",
                        'profesor1': a.profesor.nombres,
                        'profesor2': b.profesor.nombres,
                        'dia': a.get_dia_semana_display(),
                        'periodo': a.periodo,
                    })
                    ids_con_cruce.update([a.pk, b.pk])

    return cruces, ids_con_cruce


@admin_required
def asignacion_lista(request):
    query = request.GET.get('q', '')
    asignaciones = Asignacion.objects.select_related(
        'profesor', 'materia', 'programa', 'aula'
    ).all()
    if query:
        asignaciones = asignaciones.filter(
            Q(materia__nombre__icontains=query) |
            Q(profesor__nombres__icontains=query) |
            Q(programa__nombre__icontains=query)
        )

    asignaciones_list = list(asignaciones)
    cruces_detectados, ids_con_cruce = _detectar_cruces(asignaciones_list)

    # Marcar asignaciones con cruce
    for asig in asignaciones_list:
        asig.tiene_cruce = asig.pk in ids_con_cruce

    return render(request, 'asignaciones/asignacion_lista.html', {
        'asignaciones': asignaciones_list,
        'query': query,
        'cruces_detectados': cruces_detectados,
    })


@admin_required
def asignacion_crear(request):
    if request.method == 'POST':
        form = AsignacionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignación creada exitosamente.')
            return redirect('asignaciones:lista')
    else:
        form = AsignacionForm()
    return render(request, 'asignaciones/asignacion_form.html', {
        'form': form, 'titulo': 'Crear Asignación', 'accion': 'Guardar'
    })


@admin_required
def asignacion_editar(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    if request.method == 'POST':
        form = AsignacionForm(request.POST, instance=asignacion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Asignación actualizada exitosamente.')
            return redirect('asignaciones:lista')
    else:
        form = AsignacionForm(instance=asignacion)
    return render(request, 'asignaciones/asignacion_form.html', {
        'form': form, 'titulo': 'Editar Asignación', 'accion': 'Actualizar'
    })


# 🚀 VISTA ACTUALIZADA CON PROTECTED_ERROR
@admin_required
def asignacion_eliminar(request, pk):
    asignacion = get_object_or_404(Asignacion, pk=pk)
    if request.method == 'POST':
        try:
            asignacion.delete()
            messages.success(request, 'Asignación eliminada exitosamente.')
        except ProtectedError:
            # Atrapa el error y muestra la alerta amigable
            messages.error(
                request, 
                f'No se puede eliminar la asignación de "{asignacion.materia.nombre}" porque ya tiene estudiantes matriculados, asistencias o notas registradas. Te recomendamos editarla y desmarcar la casilla "Activa".'
            )
        return redirect('asignaciones:lista')
        
    return render(request, 'asignaciones/asignacion_confirmar_eliminar.html', {
        'asignacion': asignacion
    })


@admin_required
def matricular_estudiantes(request, pk):
    """Matricular estudiantes en una asignación específica."""
    asignacion = get_object_or_404(
        Asignacion.objects.select_related('profesor', 'materia', 'programa'), pk=pk
    )
    matriculados = Matricula.objects.filter(
        asignacion=asignacion, activa=True
    ).select_related('estudiante')

    if request.method == 'POST':
        form = MatriculaForm(request.POST, asignacion=asignacion)
        if form.is_valid():
            estudiantes = form.cleaned_data['estudiantes']
            count = 0
            for est in estudiantes:
                Matricula.objects.get_or_create(
                    estudiante=est, asignacion=asignacion,
                    defaults={'activa': True}
                )
                count += 1
            messages.success(request, f'{count} estudiante(s) matriculado(s) exitosamente.')
            return redirect('asignaciones:matricular', pk=pk)
    else:
        form = MatriculaForm(asignacion=asignacion)

    return render(request, 'asignaciones/matricular.html', {
        'asignacion': asignacion,
        'matriculados': matriculados,
        'form': form,
    })


@admin_required
def desmatricular_estudiante(request, pk, matricula_id):
    """Desmatricular un estudiante de una asignación."""
    matricula = get_object_or_404(Matricula, pk=matricula_id)
    matricula.activa = False
    matricula.save()
    messages.success(request, f'Estudiante desmatriculado exitosamente.')
    return redirect('asignaciones:matricular', pk=pk)


def _calcular_horas(asignaciones):
    """Calcula el total de horas semanales de un conjunto de asignaciones."""
    total_minutos = 0
    for asig in asignaciones:
        if asig.hora_inicio and asig.hora_fin:
            inicio = timedelta(hours=asig.hora_inicio.hour, minutes=asig.hora_inicio.minute)
            fin = timedelta(hours=asig.hora_fin.hour, minutes=asig.hora_fin.minute)
            total_minutos += (fin - inicio).seconds // 60
    horas = total_minutos // 60
    minutos = total_minutos % 60
    return horas, minutos, total_minutos


@login_required_custom
def horario_docentes(request):
    """Vista de todos los docentes con resumen de carga horaria."""
    if request.user.es_admin:
        profesores = Profesor.objects.filter(activo=True).order_by('nombres')
    elif request.user.es_profesor and request.user.profesor:
        profesores = Profesor.objects.filter(pk=request.user.profesor.pk)
    else:
        profesores = Profesor.objects.none()

    resumen = []
    for profesor in profesores:
        asignaciones = Asignacion.objects.filter(
            profesor=profesor, activa=True
        ).select_related('materia', 'aula')
        horas, minutos, _ = _calcular_horas(asignaciones)
        total_materias = asignaciones.count()

        # Contar días de la semana con clases
        dias_con_clase = asignaciones.exclude(
            dia_semana=''
        ).values_list('dia_semana', flat=True).distinct()

        resumen.append({
            'profesor': profesor,
            'total_materias': total_materias,
            'total_horas': horas,
            'total_minutos': minutos,
            'dias_con_clase': list(dias_con_clase),
            'num_dias': len(set(dias_con_clase)),
        })

    return render(request, 'asignaciones/horario_docentes.html', {
        'resumen': resumen,
    })


@login_required_custom
def horario_docente_detalle(request, profesor_id):
    """Vista detallada del horario semanal de un docente."""
    profesor = get_object_or_404(Profesor, pk=profesor_id)

    # Verificar permisos
    if request.user.es_profesor and request.user.profesor != profesor:
        messages.error(request, 'No tiene permisos para ver este horario.')
        return redirect('asignaciones:horario_docentes')

    asignaciones = Asignacion.objects.filter(
        profesor=profesor, activa=True
    ).select_related('materia', 'programa', 'aula').order_by('hora_inicio')

    # Organizar por día de la semana
    DIAS_ORDEN = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
    ]

    horario_semanal = []
    cruces_horario = []  # Lista de alertas de cruce

    for dia_key, dia_nombre in DIAS_ORDEN:
        asigs_dia = [a for a in asignaciones if a.dia_semana == dia_key]
        asigs_dia.sort(key=lambda a: a.hora_inicio if a.hora_inicio else '00:00')

        horas_dia, minutos_dia, _ = _calcular_horas(asigs_dia)

        # Detectar cruces dentro del mismo día para este profesor
        cruces_dia = []
        for i, a in enumerate(asigs_dia):
            if not a.hora_inicio or not a.hora_fin:
                continue
            for b in asigs_dia[i + 1:]:
                if not b.hora_inicio or not b.hora_fin:
                    continue
                # Solapamiento: A.inicio < B.fin AND A.fin > B.inicio
                if a.hora_inicio < b.hora_fin and a.hora_fin > b.hora_inicio:
                    a.tiene_cruce = True
                    b.tiene_cruce = True
                    cruces_horario.append({
                        'dia': dia_nombre,
                        'materia1': a.materia.nombre,
                        'horario1': f"{a.hora_inicio.strftime('%H:%M')}-{a.hora_fin.strftime('%H:%M')}",
                        'materia2': b.materia.nombre,
                        'horario2': f"{b.hora_inicio.strftime('%H:%M')}-{b.hora_fin.strftime('%H:%M')}",
                        'aula1': str(a.aula) if a.aula else 'Sin aula',
                        'aula2': str(b.aula) if b.aula else 'Sin aula',
                    })

        horario_semanal.append({
            'dia_key': dia_key,
            'dia_nombre': dia_nombre,
            'asignaciones': asigs_dia,
            'horas': horas_dia,
            'minutos': minutos_dia,
            'tiene_clases': len(asigs_dia) > 0,
            'tiene_cruces': len(cruces_dia) > 0,
        })

    # Totales generales
    horas_total, minutos_total, _ = _calcular_horas(asignaciones)
    dias_activos = sum(1 for d in horario_semanal if d['tiene_clases'])

    return render(request, 'asignaciones/horario_docente_detalle.html', {
        'profesor': profesor,
        'horario_semanal': horario_semanal,
        'total_materias': asignaciones.count(),
        'total_horas': horas_total,
        'total_minutos': minutos_total,
        'dias_activos': dias_activos,
        'cruces_horario': cruces_horario,
    })
