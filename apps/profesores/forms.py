"""Formularios del módulo de Profesores."""
from django import forms
from .models import Profesor


class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ['nombres', 'identificacion', 'telefono', 'correo', 'activo']
        widgets = {
            'nombres': forms.TextInput(attrs={'class': 'form-control', 'id': 'prof-nombres'}),
            'identificacion': forms.TextInput(attrs={'class': 'form-control', 'id': 'prof-identificacion'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'id': 'prof-telefono'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'id': 'prof-correo'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'prof-activo'}),
        }
