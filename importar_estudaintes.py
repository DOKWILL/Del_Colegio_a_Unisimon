import os
import io
import unicodedata
import django
import requests
import pandas as pd

# Inicializar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# IMPORTANTE: Ajusta las importaciones según la ubicación de tus modelos
from apps.estudiantes.models import Estudiante, Colegio
from apps.materias.models import Programa  # Ajusta esta ruta si tu app 'materias' está en otra ubicación


def quitar_tildes(texto):
    """Elimina tildes/acentos para comparar sin importar cómo estén escritos."""
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


# Mapea las variantes (ya sin tildes) que puedan venir en el Excel a los
# códigos exactos que acepta el modelo (max_length=4): 'T.I.', 'C.C.', 'PPT'
MAPEO_TIPO_ID = {
    'T.I.': 'T.I.', 'TI': 'T.I.', 'T.I': 'T.I.',
    'TARJETA DE IDENTIDAD': 'T.I.',
    'C.C.': 'C.C.', 'CC': 'C.C.', 'C.C': 'C.C.',
    'CEDULA': 'C.C.', 'CEDULA DE CIUDADANIA': 'C.C.', 'CEDULA CIUDADANIA': 'C.C.',
    'PPT': 'PPT',
    'PERMISO DE PROTECCION TEMPORAL': 'PPT',
}


def normalizar_tipo_id(valor):
    """Convierte cualquier variante del tipo de documento al código válido."""
    clave = quitar_tildes(str(valor).strip().upper())
    return MAPEO_TIPO_ID.get(clave)  # None si no coincide con ninguna variante conocida


def cargar_estudiantes_github(url_raw):
    try:
        print("📥 Descargando archivo desde GitHub...")
        respuesta = requests.get(url_raw)
        respuesta.raise_for_status()  # Verifica que la URL sea correcta (código 200)

        # Leer el contenido binario en memoria y pasarlo a Pandas
        df = pd.read_excel(io.BytesIO(respuesta.content)).fillna('')
        print("✅ Archivo leído exitosamente. Iniciando procesamiento...\n")
    except Exception as e:
        return print(f"❌ Error al descargar o leer el Excel: {e}")

    stats = {'creados': 0, 'omitidos': 0, 'errores': 0}

    for index, row in df.iterrows():
        doc = str(row['Identificacion']).strip()
        nombre_colegio = str(row['Colegio']).strip()
        nombre_programa = str(row['Programa']).strip()

        if not doc:
            continue

        # Buscar colegio existente
        colegio = Colegio.objects.filter(nombre__iexact=nombre_colegio).first()
        if not colegio:
            print(f"⚠️ Colegio '{nombre_colegio}' no existe. Omitiendo documento {doc}.")
            stats['errores'] += 1
            continue

        # Buscar programa existente
        programa = Programa.objects.filter(nombre__iexact=nombre_programa).first()
        if not programa:
            print(f"⚠️ Programa '{nombre_programa}' no existe. Omitiendo documento {doc}.")
            stats['errores'] += 1
            continue

        # Normalizar y validar tipo de identificación
        tipo_id = normalizar_tipo_id(row['Tipo_Doc'])
        if not tipo_id:
            print(f"⚠️ Tipo de documento '{row['Tipo_Doc']}' no reconocido. Omitiendo documento {doc}.")
            stats['errores'] += 1
            continue

        estudiante, creado = Estudiante.objects.get_or_create(
            identificacion=doc,
            defaults={
                'nombre_apellido': str(row['Nombre']).strip(),
                'tipo_identificacion': tipo_id,
                'colegio': colegio,
                'programa': programa,
                'activo': True
            }
        )

        stats['creados' if creado else 'omitidos'] += 1

    print(f"\n🏁 Proceso finalizado. Resultados: {stats}")


if __name__ == '__main__':
    # Reemplaza esta URL con el enlace RAW exacto de tu archivo en GitHub
    URL_GITHUB = 'https://raw.githubusercontent.com/DOKWILL/Del_Colegio_a_Unisimon/main/estudiantes.xlsx'

    cargar_estudiantes_github(URL_GITHUB)
