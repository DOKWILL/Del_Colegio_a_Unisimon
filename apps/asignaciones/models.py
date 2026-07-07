"""
Modelos del módulo de Asignación Académica (Módulo 5).

Define Asignacion (profesor→materia→programa→aula) y Matricula (estudiante→asignacion).
Incluye detección de cruces de horario por docente y espacio físico.
"""
from django.db import models


class Asignacion(models.Model):
    """
    Asignación académica: vincula un profesor con una materia, programa y aula.
    Es la tabla pivote central del sistema.
    """
    DIA_CHOICES = [
        ('lunes', 'Lunes'),
        ('martes', 'Martes'),
        ('miercoles', 'Miércoles'),
        ('jueves', 'Jueves'),
        ('viernes', 'Viernes'),
        ('sabado', 'Sábado'),
        ('domingo', 'Domingo'),
    ]

    profesor = models.ForeignKey(
        'profesores.Profesor', on_delete=models.PROTECT,
        related_name='asignaciones', verbose_name='Profesor'
    )
    materia = models.ForeignKey(
        'materias.Materia', on_delete=models.PROTECT,
        related_name='asignaciones', verbose_name='Materia'
    )
    programa = models.ForeignKey(
        'materias.Programa', on_delete=models.PROTECT,
        related_name='asignaciones', verbose_name='Programa'
    )
    aula = models.ForeignKey(
        'espacios.Aula', on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='asignaciones', verbose_name='Aula'
    )
    horario = models.CharField(max_length=200, blank=True, verbose_name='Horario (texto)')
    dia_semana = models.CharField(
        max_length=10, choices=DIA_CHOICES, blank=True,
        verbose_name='Día de la semana'
    )
    hora_inicio = models.TimeField(null=True, blank=True, verbose_name='Hora de inicio')
    hora_fin = models.TimeField(null=True, blank=True, verbose_name='Hora de fin')
    periodo = models.CharField(max_length=20, blank=True, verbose_name='Periodo')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        db_table = 'asignaciones'
        verbose_name = 'Asignación'
        verbose_name_plural = 'Asignaciones'
        unique_together = ['profesor', 'materia', 'programa', 'periodo']

    def __str__(self):
        return f"{self.materia} - {self.profesor} ({self.periodo})"

    def horario_display(self):
        """Muestra el horario formateado."""
        if self.dia_semana and self.hora_inicio and self.hora_fin:
            dia = self.get_dia_semana_display()
            return f"{dia} {self.hora_inicio.strftime('%H:%M')}-{self.hora_fin.strftime('%H:%M')}"
        return self.horario or '-'

    def duracion_display(self):
        """Muestra la duración de la clase (ej: '4h', '2h 30min')."""
        if self.hora_inicio and self.hora_fin:
            from datetime import timedelta
            inicio = timedelta(hours=self.hora_inicio.hour, minutes=self.hora_inicio.minute)
            fin = timedelta(hours=self.hora_fin.hour, minutes=self.hora_fin.minute)
            total_min = (fin - inicio).seconds // 60
            horas = total_min // 60
            minutos = total_min % 60
            if minutos:
                return f"{horas}h {minutos}min"
            return f"{horas}h"
        return '-'

    def hay_cruce_horario(self):
        """
        Detecta cruces de horario con otras asignaciones activas del mismo periodo.

        Returns:
            dict con:
            - 'cruces_profesor': lista de asignaciones que cruzan con el profesor
            - 'cruces_aula': lista de asignaciones que cruzan con el aula
        """
        cruces = {'cruces_profesor': [], 'cruces_aula': []}

        if not self.dia_semana or not self.hora_inicio or not self.hora_fin:
            return cruces

        # Buscar asignaciones del mismo periodo, mismo día, que se solapen en horario
        otras = Asignacion.objects.filter(
            activa=True,
            periodo=self.periodo,
            dia_semana=self.dia_semana,
        ).exclude(pk=self.pk)

        for otra in otras.select_related('profesor', 'materia', 'aula'):
            if not otra.hora_inicio or not otra.hora_fin:
                continue

            # Verificar solapamiento: [A_ini, A_fin) ∩ [B_ini, B_fin)
            if self.hora_inicio < otra.hora_fin and self.hora_fin > otra.hora_inicio:
                # Hay solapamiento temporal
                if otra.profesor_id == self.profesor_id:
                    cruces['cruces_profesor'].append(otra)
                if self.aula_id and otra.aula_id == self.aula_id:
                    cruces['cruces_aula'].append(otra)

        return cruces


class Matricula(models.Model):
    """Matrícula de un estudiante en una asignación específica."""
    estudiante = models.ForeignKey(
        'estudiantes.Estudiante', on_delete=models.PROTECT,
        related_name='matriculas', verbose_name='Estudiante'
    )
    asignacion = models.ForeignKey(
        Asignacion, on_delete=models.PROTECT,
        related_name='matriculas', verbose_name='Asignación'
    )
    fecha_matricula = models.DateField(auto_now_add=True, verbose_name='Fecha de matrícula')
    activa = models.BooleanField(default=True, verbose_name='Activa')

    class Meta:
        db_table = 'matriculas'
        verbose_name = 'Matrícula'
        verbose_name_plural = 'Matrículas'
        unique_together = ['estudiante', 'asignacion']

    def __str__(self):
        return f"{self.estudiante} → {self.asignacion.materia}"
