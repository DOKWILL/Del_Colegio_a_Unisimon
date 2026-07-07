"""Formularios del módulo de Asignación Académica con detección de cruces."""
from django import forms
from .models import Asignacion, Matricula
from apps.estudiantes.models import Estudiante


class AsignacionForm(forms.ModelForm):
    class Meta:
        model = Asignacion
        fields = [
            'profesor', 'materia', 'programa', 'aula',
            'dia_semana', 'hora_inicio', 'hora_fin',
            'horario', 'periodo', 'activa'
        ]
        widgets = {
            'profesor': forms.Select(attrs={'class': 'form-select', 'id': 'asig-profesor'}),
            'materia': forms.Select(attrs={'class': 'form-select', 'id': 'asig-materia'}),
            'programa': forms.Select(attrs={'class': 'form-select', 'id': 'asig-programa'}),
            'aula': forms.Select(attrs={'class': 'form-select', 'id': 'asig-aula'}),
            'dia_semana': forms.Select(attrs={'class': 'form-select', 'id': 'asig-dia'}),
            'hora_inicio': forms.TimeInput(attrs={
                'class': 'form-control', 'type': 'time', 'id': 'asig-hora-inicio'
            }),
            'hora_fin': forms.TimeInput(attrs={
                'class': 'form-control', 'type': 'time', 'id': 'asig-hora-fin'
            }),
            'horario': forms.TextInput(attrs={
                'class': 'form-control', 'id': 'asig-horario',
                'placeholder': 'Ej: Sábados 8:00-12:00 (descripción adicional)'
            }),
            'periodo': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'Ej: 2026-2', 'id': 'asig-periodo'
            }),
            'activa': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'asig-activa'}),
        }
        help_texts = {
            'dia_semana': 'Seleccione el día del encuentro',
            'hora_inicio': 'Hora de inicio del encuentro',
            'hora_fin': 'Hora de fin del encuentro',
            'horario': 'Descripción adicional del horario (opcional)',
        }

    def clean(self):
        cleaned_data = super().clean()
        hora_inicio = cleaned_data.get('hora_inicio')
        hora_fin = cleaned_data.get('hora_fin')
        dia_semana = cleaned_data.get('dia_semana')

        # Validar coherencia de horarios
        if hora_inicio and hora_fin and hora_inicio >= hora_fin:
            raise forms.ValidationError(
                'La hora de inicio debe ser anterior a la hora de fin.'
            )

        # Solo validar cruces si tenemos día y horas completos
        if dia_semana and hora_inicio and hora_fin:
            profesor = cleaned_data.get('profesor')
            aula = cleaned_data.get('aula')
            periodo = cleaned_data.get('periodo')
            errores = []

            # ============================================================
            # CRUCE POR DOCENTE: El mismo profesor no puede tener otra
            # clase que se solape en el mismo día y periodo.
            # Solapamiento: A.inicio < B.fin AND A.fin > B.inicio
            # Ejemplo: 8:00-12:00 cruza con 8:00-10:00 y con 10:00-12:00
            # ============================================================
            conflictos_prof = Asignacion.objects.filter(
                activa=True,
                profesor=profesor,
                periodo=periodo,
                dia_semana=dia_semana,
                hora_inicio__lt=hora_fin,   # La otra empieza antes de que esta termine
                hora_fin__gt=hora_inicio,   # La otra termina después de que esta empiece
            ).select_related('materia', 'aula')
            if self.instance.pk:
                conflictos_prof = conflictos_prof.exclude(pk=self.instance.pk)

            for conflicto in conflictos_prof:
                errores.append(
                    f'CRUCE DE DOCENTE: El profesor "{profesor}" ya tiene asignada '
                    f'"{conflicto.materia}" el {conflicto.get_dia_semana_display()} '
                    f'de {conflicto.hora_inicio.strftime("%H:%M")} a '
                    f'{conflicto.hora_fin.strftime("%H:%M")} '
                    f'(periodo {conflicto.periodo}). '
                    f'No puede asignar otra clase de {hora_inicio.strftime("%H:%M")} a '
                    f'{hora_fin.strftime("%H:%M")} porque se solapan.'
                )

            # ============================================================
            # CRUCE POR ESPACIO FÍSICO: La misma aula no puede tener
            # dos clases al mismo tiempo
            # ============================================================
            if aula:
                conflictos_aula = Asignacion.objects.filter(
                    activa=True,
                    aula=aula,
                    periodo=periodo,
                    dia_semana=dia_semana,
                    hora_inicio__lt=hora_fin,
                    hora_fin__gt=hora_inicio,
                ).select_related('materia', 'profesor')
                if self.instance.pk:
                    conflictos_aula = conflictos_aula.exclude(pk=self.instance.pk)

                for conflicto in conflictos_aula:
                    errores.append(
                        f'CRUCE DE ESPACIO FÍSICO: El aula "{aula}" ya está asignada '
                        f'a "{conflicto.materia}" con el profesor "{conflicto.profesor}" '
                        f'el {conflicto.get_dia_semana_display()} '
                        f'de {conflicto.hora_inicio.strftime("%H:%M")} a '
                        f'{conflicto.hora_fin.strftime("%H:%M")} '
                        f'(periodo {conflicto.periodo}).'
                    )

            if errores:
                raise forms.ValidationError(errores)

        return cleaned_data


class MatriculaForm(forms.Form):
    """Formulario para matricular estudiantes en una asignación."""
    estudiantes = forms.ModelMultipleChoiceField(
        queryset=Estudiante.objects.filter(activo=True),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Estudiantes disponibles'
    )

    def __init__(self, *args, asignacion=None, **kwargs):
        super().__init__(*args, **kwargs)
        if asignacion:
            ya_matriculados = Matricula.objects.filter(
                asignacion=asignacion, activa=True
            ).values_list('estudiante_id', flat=True)
            self.fields['estudiantes'].queryset = Estudiante.objects.filter(
                activo=True,
                programa=asignacion.programa
            ).exclude(id__in=ya_matriculados)
