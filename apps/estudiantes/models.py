"""
Modelos del módulo de Estudiantes (Módulo 1).

Define los modelos Colegio y Estudiante con sus relaciones
al programa académico y colegio de procedencia.
"""
from django.db import models


class Colegio(models.Model):
    """Colegio de procedencia de los estudiantes."""
    nombre = models.CharField(max_length=200, verbose_name='Nombre del colegio')
    ciudad = models.CharField(max_length=100, default='Barranquilla', verbose_name='Ciudad')

    class Meta:
        db_table = 'colegios'
        verbose_name = 'Colegio'
        verbose_name_plural = 'Colegios'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Estudiante(models.Model):
    """Estudiante matriculado en el programa."""
    TIPO_ID_CHOICES = [
        ('T.I.', 'Tarjeta de Identidad'),
        ('C.C.', 'Cédula de Ciudadanía'),
    ]

    nombre_apellido = models.CharField(max_length=200, verbose_name='Nombre y Apellido')
    tipo_identificacion = models.CharField(
        max_length=4, choices=TIPO_ID_CHOICES, default='T.I.',
        verbose_name='Tipo de Identificación'
    )
    identificacion = models.CharField(max_length=20, unique=True, verbose_name='Identificación')
    programa = models.ForeignKey(
        'materias.Programa', on_delete=models.PROTECT,
        related_name='estudiantes', verbose_name='Programa'
    )
    colegio = models.ForeignKey(
        Colegio, on_delete=models.PROTECT,
        related_name='estudiantes', verbose_name='Colegio'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    fecha_registro = models.DateField(auto_now_add=True, verbose_name='Fecha de registro')

    class Meta:
        db_table = 'estudiantes'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'
        ordering = ['nombre_apellido']

    def __str__(self):
        return f"{self.nombre_apellido} ({self.identificacion})"
