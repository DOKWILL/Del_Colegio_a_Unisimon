"""Modelo del módulo de Asistencia (Módulo 6)."""
from django.db import models


class Asistencia(models.Model):
    """Registro de asistencia de un estudiante a un encuentro."""
    ESTADO_CHOICES = [
        ('presente', 'Presente'),
        ('ausente', 'Ausente'),
        ('excusa', 'Excusa'),
        ('retardo', 'Retardo'),
    ]

    asignacion = models.ForeignKey(
        'asignaciones.Asignacion', on_delete=models.PROTECT,
        related_name='asistencias', verbose_name='Asignación'
    )
    estudiante = models.ForeignKey(
        'estudiantes.Estudiante', on_delete=models.PROTECT,
        related_name='asistencias', verbose_name='Estudiante'
    )
    fecha = models.DateField(verbose_name='Fecha')
    hora = models.TimeField(auto_now_add=True, verbose_name='Hora')
    encuentro = models.PositiveIntegerField(verbose_name='Número de encuentro')
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='presente', verbose_name='Estado')
    observaciones = models.TextField(blank=True, verbose_name='Observaciones')

    class Meta:
        db_table = 'asistencia'
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ['asignacion', 'estudiante', 'encuentro']
        ordering = ['-fecha', 'estudiante__nombre_apellido']

    def __str__(self):
        return f"{self.estudiante} - {self.get_estado_display()} ({self.fecha})"
