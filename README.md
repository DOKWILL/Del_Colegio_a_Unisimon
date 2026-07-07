# 🎓 Sistema de Gestión Académica — Del Colegio a Unisimón

**Universidad Simón Bolívar**

Sistema web profesional para el control académico del programa "Del Colegio a Unisimón". Permite administrar estudiantes, profesores, materias, programas, espacios físicos, asistencia y calificaciones.

## 🚀 Características

- **Dashboard** con KPIs y gráficos interactivos (Chart.js)
- **9 módulos**: Estudiantes, Profesores, Materias, Espacios, Asignaciones, Asistencia, Notas, Reportes, Usuarios
- **Control de roles**: Administrador (acceso total) y Profesor (solo sus cursos)
- **Asistencia**: Registro por encuentro con cálculo automático de porcentajes
- **Calificaciones**: Parciales (30%, 30%, 40%) con nota definitiva automática
- **Reportes**: PDF y Excel profesionales con estadísticas
- **Nota mínima configurable** desde el panel de administración
- **Modo oscuro** con persistencia
- **Responsive** y móvil-friendly
- **Seguridad**: CSRF, XSS, hash de contraseñas, control por roles

## 📋 Requisitos

- Python 3.10+
- pip

## ⚡ Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/colegio-unisimon.git
cd colegio-unisimon

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Copiar variables de entorno
copy .env.example .env      # Windows
# cp .env.example .env      # Linux/Mac

# 5. Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# 6. Cargar datos de prueba
python seed/seed_data.py

# 7. Ejecutar servidor
python manage.py runserver
```

## 🔑 Credenciales de Prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| `admin` | `admin123` | Administrador |
| `profesor1` | `prof123` | Profesor |
| `profesor2` | `prof123` | Profesor |
| `profesor3` | `prof123` | Profesor |

## 🏗️ Estructura del Proyecto

```
colegio_unisimon/
├── config/              # Configuración Django
├── apps/
│   ├── auth_app/        # Módulo 9: Usuarios y autenticación
│   ├── dashboard/       # Dashboard principal
│   ├── estudiantes/     # Módulo 1: Gestión de estudiantes
│   ├── profesores/      # Módulo 2: Gestión de profesores
│   ├── materias/        # Módulo 3: Gestión de materias y programas
│   ├── espacios/        # Módulo 4: Gestión de espacios físicos
│   ├── asignaciones/    # Módulo 5: Asignación académica
│   ├── asistencia/      # Módulo 6: Control de asistencia
│   ├── notas/           # Módulo 7: Registro de calificaciones
│   └── reportes/        # Módulo 8: Generación de reportes
├── templates/           # Templates HTML
├── static/              # CSS, JS, imágenes
├── seed/                # Datos de prueba
└── manage.py
```

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.12, Django 5.1 |
| Frontend | Bootstrap 5.3, FontAwesome 6, Chart.js 4, DataTables |
| Base de datos | SQLite (dev) / PostgreSQL (prod) |
| Reportes | ReportLab (PDF), openpyxl (Excel) |
| Despliegue | Gunicorn, WhiteNoise |

## 📄 Licencia

Universidad Simón Bolívar © 2026. Todos los derechos reservados.
