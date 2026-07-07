"""
Modelo del módulo de Calificaciones (Módulo 7).

Cada nota tiene tres parciales con pesos 30%, 30%, 40%.
La definitiva y el estado se calculan automáticamente.
"""
from django.db import models
from apps.auth_app.models import ConfiguracionSistema


class Nota(models.Model):
    """Registro de calificaciones de un estudiante en una asignación."""
    asignacion = models.ForeignKey(
        'asignaciones.Asignacion', on_delete=models.PROTECT,
        related_name='notas', verbose_name='Asignación'
    )
    estudiante = models.ForeignKey(
        'estudiantes.Estudiante', on_delete=models.PROTECT,
        related_name='notas', verbose_name='Estudiante'
    )
    parcial1 = models.FloatField(null=True, blank=True, verbose_name='Parcial 1 (30%)')
    parcial2 = models.FloatField(null=True, blank=True, verbose_name='Parcial 2 (30%)')
    parcial3 = models.FloatField(null=True, blank=True, verbose_name='Parcial 3 (40%)')
    definitiva = models.FloatField(null=True, blank=True, verbose_name='Definitiva')
    estado = models.CharField(max_length=20, blank=True, verbose_name='Estado')

    class Meta:
        db_table = 'notas'
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'
        unique_together = ['asignacion', 'estudiante']
        ordering = ['estudiante__nombre_apellido']

    def __str__(self):
        return f"{self.estudiante} - Def: {self.definitiva}"

    def calcular_definitiva(self):
        """Calcula la nota definitiva: P1×0.30 + P2×0.30 + P3×0.40"""
        p1 = self.parcial1 or 0
        p2 = self.parcial2 or 0
        p3 = self.parcial3 or 0
        self.definitiva = round(p1 * 0.30 + p2 * 0.30 + p3 * 0.40, 2)

        nota_minima = ConfiguracionSistema.get_nota_minima()
        self.estado = 'Aprobado' if self.definitiva >= nota_minima else 'Reprobado'

    def save(self, *args, **kwargs):
        """Recalcula la definitiva antes de guardar."""
        self.calcular_definitiva()
        super().save(*args, **kwargs)
