"""
Script de datos de prueba (seed) para el sistema.

Crea: roles, usuarios, programas, colegios, sedes, aulas, profesores,
materias, estudiantes, asignaciones, matrículas, asistencias y notas.

Uso: python manage.py shell < seed/seed_data.py
"""
import os
import sys
import django
from datetime import date, timedelta
import random

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.auth_app.models import Rol, Usuario, ConfiguracionSistema
from apps.profesores.models import Profesor
from apps.estudiantes.models import Colegio, Estudiante
from apps.materias.models import Programa, Materia
from apps.espacios.models import Sede, Aula
from apps.asignaciones.models import Asignacion, Matricula
from apps.asistencia.models import Asistencia
from apps.notas.models import Nota

print("=" * 60)
print("  Cargando datos de prueba...")
print("  Del Colegio a Unisimón")
print("=" * 60)

# === ROLES ===
print("\n→ Creando roles...")
rol_admin, _ = Rol.objects.get_or_create(nombre=Rol.ADMIN)
rol_profesor, _ = Rol.objects.get_or_create(nombre=Rol.PROFESOR)
print(f"  ✓ Roles creados: {Rol.objects.count()}")

# === CONFIGURACIÓN ===
print("\n→ Configuración del sistema...")
ConfiguracionSistema.objects.update_or_create(
    clave='nota_minima_aprobatoria',
    defaults={'valor': '3.0', 'descripcion': 'Nota mínima para aprobar (0-5)'}
)
print("  ✓ Nota mínima aprobatoria: 3.0")

# === ADMIN USER ===
print("\n→ Creando usuario administrador...")
if not Usuario.objects.filter(username='admin').exists():
    admin_user = Usuario.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@unisimon.edu.co',
        first_name='Administrador',
        last_name='Sistema',
        rol=rol_admin,
    )
    print(f"  ✓ Admin: admin / admin123")
else:
    print("  ✓ Admin ya existe")

# === SEDES ===
print("\n→ Creando sedes...")
sedes_data = [
    ('Sede Principal', 'Cra. 54 No. 59-102, Barranquilla'),
    ('Sede Posgrados', 'Cra. 54 No. 64-223, Barranquilla'),
    ('Sede Cúcuta', 'Av. 3 No. 13-34, Cúcuta'),
]
sedes = []
for nombre, direccion in sedes_data:
    sede, _ = Sede.objects.get_or_create(nombre=nombre, defaults={'direccion': direccion})
    sedes.append(sede)
print(f"  ✓ Sedes creadas: {len(sedes)}")

# === AULAS ===
print("\n→ Creando aulas...")
aulas_data = [
    ('Aula 101', sedes[0], 35, 'Aula multimedia'),
    ('Aula 202', sedes[0], 40, 'Aula de cómputo'),
    ('Aula 301', sedes[0], 30, 'Aula regular'),
    ('Auditorio A', sedes[0], 120, 'Auditorio principal'),
    ('Lab. Sistemas', sedes[0], 25, 'Laboratorio de sistemas'),
    ('Aula 105', sedes[1], 30, 'Aula posgrados'),
]
aulas = []
for nombre, sede, cap, desc in aulas_data:
    aula, _ = Aula.objects.get_or_create(
        nombre=nombre, sede=sede,
        defaults={'capacidad': cap, 'descripcion': desc}
    )
    aulas.append(aula)
print(f"  ✓ Aulas creadas: {len(aulas)}")

# === COLEGIOS ===
print("\n→ Creando colegios...")
colegios_data = [
    ('Colegio Distrital de Barranquilla', 'Barranquilla'),
    ('Colegio La Sagrada Familia', 'Barranquilla'),
    ('I.E. María Auxiliadora', 'Barranquilla'),
    ('Colegio Americano', 'Barranquilla'),
    ('I.E. San José', 'Soledad'),
    ('Colegio INEM', 'Barranquilla'),
    ('I.E. Las Nieves', 'Barranquilla'),
]
colegios = []
for nombre, ciudad in colegios_data:
    col, _ = Colegio.objects.get_or_create(nombre=nombre, defaults={'ciudad': ciudad})
    colegios.append(col)
print(f"  ✓ Colegios creados: {len(colegios)}")

# === PROGRAMAS ===
print("\n→ Creando programas...")
programas_data = [
    ('Ingeniería de Sistemas', 'ISI'),
    ('Administración de Empresas', 'ADE'),
    ('Derecho', 'DER'),
    ('Psicología', 'PSI'),
    ('Ingeniería Industrial', 'IIN'),
]
programas = []
for nombre, codigo in programas_data:
    prog, _ = Programa.objects.get_or_create(nombre=nombre, defaults={'codigo': codigo})
    programas.append(prog)
print(f"  ✓ Programas creados: {len(programas)}")

# === PROFESORES ===
print("\n→ Creando profesores...")
profesores_data = [
    ('Carlos Eduardo Martínez Pérez', '1045678901', '3001234567', 'carlos.martinez@unisimon.edu.co'),
    ('María Isabel Rodríguez Herrera', '1098765432', '3009876543', 'maria.rodriguez@unisimon.edu.co'),
    ('Juan Pablo Gómez Díaz', '1087654321', '3004567890', 'juan.gomez@unisimon.edu.co'),
    ('Ana Lucía Torres Mendoza', '1076543210', '3007654321', 'ana.torres@unisimon.edu.co'),
    ('Roberto Andrés Silva Castillo', '1065432109', '3002345678', 'roberto.silva@unisimon.edu.co'),
]
profesores = []
for nombres, iden, tel, correo in profesores_data:
    prof, _ = Profesor.objects.get_or_create(
        identificacion=iden,
        defaults={'nombres': nombres, 'telefono': tel, 'correo': correo}
    )
    profesores.append(prof)
print(f"  ✓ Profesores creados: {len(profesores)}")

# === CREAR USUARIOS PARA PROFESORES ===
print("\n→ Creando usuarios de profesores...")
for i, prof in enumerate(profesores):
    username = f'profesor{i+1}'
    if not Usuario.objects.filter(username=username).exists():
        user = Usuario.objects.create_user(
            username=username,
            password='prof123',
            first_name=prof.nombres.split()[0],
            last_name=' '.join(prof.nombres.split()[1:]),
            email=prof.correo,
            rol=rol_profesor,
            profesor=prof,
        )
        print(f"  ✓ {username} / prof123 → {prof.nombres}")

# === MATERIAS ===
print("\n→ Creando materias...")
materias_data = [
    ('MAT101', 'Cálculo Diferencial', programas[0], 4, '2026-1'),
    ('FIS101', 'Física Mecánica', programas[0], 3, '2026-1'),
    ('PRG101', 'Programación Básica', programas[0], 3, '2026-1'),
    ('ADM101', 'Fundamentos de Administración', programas[1], 3, '2026-1'),
    ('CON101', 'Contabilidad General', programas[1], 3, '2026-1'),
    ('DER101', 'Introducción al Derecho', programas[2], 4, '2026-1'),
    ('DER201', 'Derecho Constitucional', programas[2], 3, '2026-1'),
    ('PSI101', 'Psicología General', programas[3], 3, '2026-1'),
    ('IND101', 'Procesos Industriales', programas[4], 3, '2026-1'),
    ('IND201', 'Gestión de Calidad', programas[4], 3, '2026-1'),
]
materias = []
for codigo, nombre, programa, creditos, periodo in materias_data:
    mat, _ = Materia.objects.get_or_create(
        codigo=codigo,
        defaults={'nombre': nombre, 'programa': programa, 'creditos': creditos, 'periodo': periodo}
    )
    materias.append(mat)
print(f"  ✓ Materias creadas: {len(materias)}")

# === ESTUDIANTES ===
print("\n→ Creando estudiantes...")
nombres_m = ['Andrés', 'David', 'Miguel', 'Santiago', 'Sebastián', 'Daniel', 'Mateo', 'Nicolás', 'Samuel', 'Alejandro',
             'Julián', 'Felipe', 'Emmanuel', 'Tomás', 'Gabriel', 'Camilo', 'Esteban', 'Ricardo', 'Cristian', 'Fabián']
nombres_f = ['Valentina', 'Sofía', 'Isabella', 'Mariana', 'Gabriela', 'Daniela', 'Laura', 'Natalia', 'Camila', 'Andrea',
             'Paula', 'Lorena', 'Carolina', 'Diana', 'Fernanda', 'Juliana', 'Sara', 'Melissa', 'Lucía', 'Alexandra']
apellidos = ['García', 'Martínez', 'López', 'Rodríguez', 'Hernández', 'González', 'Díaz', 'Morales', 'Torres', 'Ramírez',
             'Pérez', 'Sánchez', 'Jiménez', 'Romero', 'Vargas', 'Castro', 'Ortiz', 'Ruiz', 'Mendoza', 'Herrera']

estudiantes = []
for i in range(50):
    if i % 2 == 0:
        nombre = random.choice(nombres_m)
    else:
        nombre = random.choice(nombres_f)
    apellido1 = random.choice(apellidos)
    apellido2 = random.choice(apellidos)
    nombre_completo = f"{nombre} {apellido1} {apellido2}"
    iden = f"100{random.randint(1000000, 9999999)}"
    tipo = random.choice(['T.I.', 'C.C.'])
    programa = random.choice(programas)
    colegio = random.choice(colegios)

    est, created = Estudiante.objects.get_or_create(
        identificacion=iden,
        defaults={
            'nombre_apellido': nombre_completo,
            'tipo_identificacion': tipo,
            'programa': programa,
            'colegio': colegio,
        }
    )
    estudiantes.append(est)
print(f"  ✓ Estudiantes creados: {len(estudiantes)}")

# === ASIGNACIONES ===
print("\n→ Creando asignaciones académicas...")
asignaciones = []
asignacion_map = [
    (profesores[0], materias[0], programas[0], aulas[0]),
    (profesores[0], materias[1], programas[0], aulas[1]),
    (profesores[1], materias[2], programas[0], aulas[2]),
    (profesores[2], materias[3], programas[1], aulas[3]),
    (profesores[2], materias[4], programas[1], aulas[0]),
    (profesores[3], materias[5], programas[2], aulas[1]),
    (profesores[3], materias[6], programas[2], aulas[2]),
    (profesores[4], materias[7], programas[3], aulas[3]),
    (profesores[1], materias[8], programas[4], aulas[4]),
    (profesores[4], materias[9], programas[4], aulas[5]),
]
for prof, mat, prog, aula in asignacion_map:
    asig, _ = Asignacion.objects.get_or_create(
        profesor=prof, materia=mat, programa=prog, periodo='2026-1',
        defaults={'aula': aula, 'horario': 'Lun-Mie 8:00-10:00'}
    )
    asignaciones.append(asig)
print(f"  ✓ Asignaciones creadas: {len(asignaciones)}")

# === MATRÍCULAS ===
print("\n→ Matriculando estudiantes...")
count_matriculas = 0
for est in estudiantes:
    # Matricular en asignaciones del mismo programa
    asigs_programa = [a for a in asignaciones if a.programa == est.programa]
    for asig in asigs_programa:
        mat, created = Matricula.objects.get_or_create(
            estudiante=est, asignacion=asig
        )
        if created:
            count_matriculas += 1
print(f"  ✓ Matrículas creadas: {count_matriculas}")

# === ASISTENCIA ===
print("\n→ Generando registros de asistencia...")
estados = ['presente', 'presente', 'presente', 'presente', 'ausente', 'retardo', 'excusa']
count_asistencia = 0
for asig in asignaciones:
    matriculas = Matricula.objects.filter(asignacion=asig, activa=True)
    for encuentro in range(1, 6):
        fecha = date.today() - timedelta(days=(5 - encuentro) * 7)
        for mat in matriculas:
            Asistencia.objects.get_or_create(
                asignacion=asig,
                estudiante=mat.estudiante,
                encuentro=encuentro,
                defaults={
                    'fecha': fecha,
                    'estado': random.choice(estados),
                }
            )
            count_asistencia += 1
print(f"  ✓ Registros de asistencia: {count_asistencia}")

# === NOTAS ===
print("\n→ Generando calificaciones...")
count_notas = 0
for asig in asignaciones:
    matriculas = Matricula.objects.filter(asignacion=asig, activa=True)
    for mat in matriculas:
        nota, created = Nota.objects.get_or_create(
            asignacion=asig,
            estudiante=mat.estudiante,
            defaults={
                'parcial1': round(random.uniform(1.5, 5.0), 1),
                'parcial2': round(random.uniform(1.5, 5.0), 1),
                'parcial3': round(random.uniform(1.5, 5.0), 1),
            }
        )
        if created:
            nota.save()  # Triggers calcular_definitiva
            count_notas += 1
print(f"  ✓ Notas creadas: {count_notas}")

print("\n" + "=" * 60)
print("  ✅ Datos de prueba cargados exitosamente!")
print("=" * 60)
print(f"\n  📊 Resumen:")
print(f"     Roles:        {Rol.objects.count()}")
print(f"     Usuarios:     {Usuario.objects.count()}")
print(f"     Profesores:   {Profesor.objects.count()}")
print(f"     Programas:    {Programa.objects.count()}")
print(f"     Materias:     {Materia.objects.count()}")
print(f"     Colegios:     {Colegio.objects.count()}")
print(f"     Sedes:        {Sede.objects.count()}")
print(f"     Aulas:        {Aula.objects.count()}")
print(f"     Estudiantes:  {Estudiante.objects.count()}")
print(f"     Asignaciones: {Asignacion.objects.count()}")
print(f"     Matrículas:   {Matricula.objects.count()}")
print(f"     Asistencias:  {Asistencia.objects.count()}")
print(f"     Notas:        {Nota.objects.count()}")
print(f"\n  🔑 Credenciales:")
print(f"     Admin:    admin / admin123")
print(f"     Profesor: profesor1 / prof123")
print(f"              profesor2 / prof123")
print(f"              profesor3 / prof123")
print(f"              profesor4 / prof123")
print(f"              profesor5 / prof123")
print()
