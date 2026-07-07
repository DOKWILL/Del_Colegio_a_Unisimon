"""
Modelos de autenticación y gestión de usuarios.

Define el modelo de Usuario personalizado extendiendo AbstractUser de Django,
con soporte para roles (Administrador/Profesor) y asociación con profesor.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class Rol(models.Model):
    """Roles del sistema: Administrador o Profesor."""
    ADMIN = 'administrador'
    PROFESOR = 'profesor'

    CHOICES = [
        (ADMIN, 'Administrador'),
        (PROFESOR, 'Profesor'),
    ]

    nombre = models.CharField(max_length=20, unique=True, choices=CHOICES)

    class Meta:
        db_table = 'roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.get_nombre_display()


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado.

    Extiende AbstractUser para agregar:
    - Relación con Rol (administrador/profesor)
    - Relación opcional con Profesor
    - Campo de bloqueo de cuenta
    """
    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Rol'
    )
    profesor = models.OneToOneField(
        'profesores.Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuario',
        verbose_name='Profesor asociado'
    )
    bloqueado = models.BooleanField(
        default=False,
        verbose_name='Cuenta bloqueada'
    )
    debe_cambiar_password = models.BooleanField(
        default=False,
        verbose_name='Debe cambiar contraseña',
        help_text='Se activa automáticamente al crear el usuario. '
                  'Obliga a cambiar la contraseña en el primer inicio de sesión.'
    )

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.username} ({self.rol})"

    @property
    def es_admin(self):
        """Verifica si el usuario tiene rol de administrador."""
        return self.rol and self.rol.nombre == Rol.ADMIN

    @property
    def es_profesor(self):
        """Verifica si el usuario tiene rol de profesor."""
        return self.rol and self.rol.nombre == Rol.PROFESOR

    @property
    def esta_activo(self):
        """Verifica si la cuenta está activa y no bloqueada."""
        return self.is_active and not self.bloqueado


class ConfiguracionSistema(models.Model):
    """
    Tabla de configuración global del sistema.

    Almacena parámetros configurables como la nota mínima aprobatoria.
    Cada registro es un par clave-valor con descripción.
    """
    clave = models.CharField(max_length=100, unique=True, verbose_name='Clave')
    valor = models.CharField(max_length=255, verbose_name='Valor')
    descripcion = models.TextField(blank=True, verbose_name='Descripción')

    class Meta:
        db_table = 'configuracion_sistema'
        verbose_name = 'Configuración del Sistema'
        verbose_name_plural = 'Configuraciones del Sistema'

    def __str__(self):
        return f"{self.clave}: {self.valor}"

    @classmethod
    def get_nota_minima(cls):
        """Obtiene la nota mínima aprobatoria configurada. Default: 3.0"""
        try:
            config = cls.objects.get(clave='nota_minima_aprobatoria')
            return float(config.valor)
        except (cls.DoesNotExist, ValueError):
            return 3.0
