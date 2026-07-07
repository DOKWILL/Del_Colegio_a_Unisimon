"""Formularios del módulo de Materias."""
from django import forms
from .models import Materia, Programa


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['codigo', 'nombre', 'programa', 'creditos', 'periodo', 'activo']
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'id': 'mat-codigo'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'mat-nombre'}),
            'programa': forms.Select(attrs={'class': 'form-select', 'id': 'mat-programa'}),
            'creditos': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'id': 'mat-creditos'}),
            'periodo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2026-1', 'id': 'mat-periodo'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'mat-activo'}),
        }


class ProgramaForm(forms.ModelForm):
    class Meta:
        model = Programa
        fields = ['nombre', 'codigo', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'prog-nombre'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'id': 'prog-codigo'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'prog-activo'}),
        }
