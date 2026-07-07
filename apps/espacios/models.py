"""Modelos del módulo de Espacios Físicos (Módulo 4)."""
from django.db import models


class Sede(models.Model):
    """Sede o campus de la universidad."""
    nombre = models.CharField(max_length=200, verbose_name='Nombre de la sede')
    direccion = models.CharField(max_length=300, blank=True, verbose_name='Dirección')

    class Meta:
        db_table = 'sedes'
        verbose_name = 'Sede'
        verbose_name_plural = 'Sedes'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Aula(models.Model):
    """Aula o espacio físico dentro de una sede."""
    nombre = models.CharField(max_length=100, verbose_name='Nombre del aula')
    sede = models.ForeignKey(
        Sede, on_delete=models.PROTECT,
        related_name='aulas', verbose_name='Sede'
    )
    capacidad = models.PositiveIntegerField(default=30, verbose_name='Capacidad')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    class Meta:
        db_table = 'aulas'
        verbose_name = 'Aula'
        verbose_name_plural = 'Aulas'
        ordering = ['sede', 'nombre']

    def __str__(self):
        return f"{self.nombre} - {self.sede.nombre}"
