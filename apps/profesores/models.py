"""Modelo del módulo de Profesores (Módulo 2)."""
from django.db import models


class Profesor(models.Model):
    """Profesor del programa académico."""
    nombres = models.CharField(max_length=200, verbose_name='Nombres')
    identificacion = models.CharField(max_length=20, unique=True, verbose_name='Identificación')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    correo = models.EmailField(blank=True, verbose_name='Correo electrónico')
    activo = models.BooleanField(default=True, verbose_name='Activo')

    class Meta:
        db_table = 'profesores'
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'
        ordering = ['nombres']

    def __str__(self):
        return self.nombres
