"""Formularios del módulo de Espacios Físicos."""
from django import forms
from .models import Sede, Aula


class SedeForm(forms.ModelForm):
    class Meta:
        model = Sede
        fields = ['nombre', 'direccion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'sede-nombre'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'id': 'sede-direccion'}),
        }


class AulaForm(forms.ModelForm):
    class Meta:
        model = Aula
        fields = ['nombre', 'sede', 'capacidad', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'id': 'aula-nombre'}),
            'sede': forms.Select(attrs={'class': 'form-select', 'id': 'aula-sede'}),
            'capacidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'id': 'aula-capacidad'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'id': 'aula-descripcion'}),
        }
