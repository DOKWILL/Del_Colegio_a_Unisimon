"""
Formularios de autenticación y gestión de usuarios.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import Usuario, Rol


class LoginForm(AuthenticationForm):
    """Formulario de inicio de sesión personalizado con estilos Bootstrap."""
    username = forms.CharField(
        label='Usuario',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario',
            'autofocus': True,
            'id': 'login-username',
        })
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña',
            'id': 'login-password',
        })
    )


class UsuarioCreateForm(forms.ModelForm):
    """Formulario para crear un nuevo usuario."""
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese la contraseña',
            'id': 'usuario-password',
        })
    )
    password_confirm = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la contraseña',
            'id': 'usuario-password-confirm',
        })
    )

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'profesor', 'is_active']
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'rol': 'Rol',
            'profesor': 'Profesor asociado',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'id': 'usuario-username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'usuario-firstname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'usuario-lastname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'usuario-email'}),
            'rol': forms.Select(attrs={'class': 'form-select', 'id': 'usuario-rol'}),
            'profesor': forms.Select(attrs={'class': 'form-select', 'id': 'usuario-profesor'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'usuario-activo'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.debe_cambiar_password = True
        if commit:
            user.save()
        return user


class UsuarioEditForm(forms.ModelForm):
    """Formulario para editar un usuario existente (sin cambiar contraseña)."""

    class Meta:
        model = Usuario
        fields = ['username', 'first_name', 'last_name', 'email', 'rol', 'profesor', 'is_active', 'bloqueado', 'debe_cambiar_password']
        labels = {
            'username': 'Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'rol': 'Rol',
            'profesor': 'Profesor asociado',
            'is_active': 'Activo',
            'bloqueado': 'Bloqueado',
            'debe_cambiar_password': 'Debe cambiar contraseña',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'rol': forms.Select(attrs={'class': 'form-select'}),
            'profesor': forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'bloqueado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'debe_cambiar_password': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class CambiarPasswordForm(forms.Form):
    """Formulario para cambiar la contraseña de un usuario."""
    nueva_password = forms.CharField(
        label='Nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nueva contraseña',
            'id': 'cambiar-password',
        })
    )
    confirmar_password = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme la nueva contraseña',
            'id': 'confirmar-password',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_password')
        confirmar = cleaned_data.get('confirmar_password')
        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data


class MiPasswordForm(forms.Form):
    """Formulario para que el profesor cambie su propia contraseña (primer inicio)."""
    password_actual = forms.CharField(
        label='Contraseña actual',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su contraseña actual',
            'id': 'mi-password-actual',
        })
    )
    nueva_password = forms.CharField(
        label='Nueva contraseña',
        min_length=8,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Mínimo 8 caracteres',
            'id': 'mi-password-nueva',
        })
    )
    confirmar_password = forms.CharField(
        label='Confirmar nueva contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Repita la nueva contraseña',
            'id': 'mi-password-confirmar',
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        nueva = cleaned_data.get('nueva_password')
        confirmar = cleaned_data.get('confirmar_password')
        if nueva and confirmar and nueva != confirmar:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data


class ConfiguracionForm(forms.Form):
    """Formulario para configurar la nota mínima aprobatoria."""
    nota_minima = forms.FloatField(
        label='Nota mínima aprobatoria',
        min_value=0.0,
        max_value=5.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1',
            'id': 'config-nota-minima',
        })
    )
