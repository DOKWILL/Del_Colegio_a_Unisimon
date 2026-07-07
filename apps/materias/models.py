"""Modelos del módulo de Materias y Programas (Módulo 3)."""
from django.db import models


class Programa(models.Model):
    """Programa académico del proyecto Del Colegio a Unisimón."""
    nombre = models.CharField(max_length=200, verbose_name='Nombre del programa')
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'programas'
        verbose_name = 'Programa'
        verbose_name_plural = 'Programas'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Materia(models.Model):
    """Materia o asignatura del programa."""
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código de materia')
    nombre = models.CharField(max_length=200, verbose_name='Nombre de materia')
    programa = models.ForeignKey(
        Programa, on_delete=models.PROTECT,
        related_name='materias', verbose_name='Programa'
    )
    creditos = models.PositiveIntegerField(default=1, verbose_name='Número de créditos')
    periodo = models.CharField(max_length=20, blank=True, verbose_name='Periodo')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
