"""Formularios del módulo de Estudiantes."""
from django import forms
from .models import Estudiante, Colegio


class EstudianteForm(forms.ModelForm):
    """Formulario para crear/editar estudiantes."""
    class Meta:
        model = Estudiante
        fields = ['nombre_apellido', 'tipo_identificacion', 'identificacion',
                  'programa', 'colegio', 'activo']
        widgets = {
            'nombre_apellido': forms.TextInput(attrs={'class': 'form-control', 'id': 'est-nombre'}),
            'tipo_identificacion': forms.Select(attrs={'class': 'form-select', 'id': 'est-tipo-id'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'id': 'est-identificacion'}),
            'programa': forms.Select(attrs={'class': 'form-select', 'id': 'est-programa'}),
            'colegio': forms.Select(attrs={'class': 'form-select', 'id': 'est-colegio'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'est-activo'}),
        }


class ColegioForm(forms.ModelForm):
    """Formulario para crear/editar colegios."""
    class Meta:
        model = Colegio
        fields = ['nombre', 'ciudad']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'col-nombre'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control', 'id': 'col-ciudad'}),
        }
