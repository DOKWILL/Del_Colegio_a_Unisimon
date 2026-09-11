import os
import io
import django
import requests
import pandas as pd

# Inicializar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# IMPORTANTE: Ajusta las importaciones según la ubicación de tus modelos
from apps.estudiantes.models import Estudiante
from apps.espacios.models import Colegio 

def cargar_estudiantes_github(url_raw):
    try:
        print("📥 Descargando archivo desde GitHub...")
        respuesta = requests.get(url_raw)
        respuesta.raise_for_status() # Verifica que la URL sea correcta (código 200)
        
        # Leer el contenido binario en memoria y pasarlo a Pandas
        df = pd.read_excel(io.BytesIO(respuesta.content)).fillna('')
        print("✅ Archivo leído exitosamente. Iniciando procesamiento...\n")
    except Exception as e:
        return print(f"❌ Error al descargar o leer el Excel: {e}")

    stats = {'creados': 0, 'omitidos': 0, 'errores': 0}

    for index, row in df.iterrows():
        doc = str(row['Identificacion']).strip()
        nombre_colegio = str(row['Colegio']).strip()

        if not doc: 
            continue

        colegio = Colegio.objects.filter(nombre__iexact=nombre_colegio).first()
        
        if not colegio:
            print(f"⚠️ Colegio '{nombre_colegio}' no existe. Omitiendo documento {doc}.")
            stats['errores'] += 1
            continue

        estudiante, creado = Estudiante.objects.get_or_create(
            identificacion=doc,
            defaults={
                'nombre_apellido': str(row['Nombre']).strip(),
                'tipo_identificacion': str(row['Tipo_Doc']).strip().upper(),
                'colegio': colegio,
                'programa': str(row['Programa']).strip(),
                'activo': True
            }
        )
        
        stats['creados' if creado else 'omitidos'] += 1

    print(f"\n🏁 Proceso finalizado. Resultados: {stats}")

if __name__ == '__main__':
    # Reemplaza esta URL con el enlace RAW exacto de tu archivo en GitHub
    URL_GITHUB = 'https://raw.githubusercontent.com/DOKWILL/Del_Colegio_a_Unisimon/main/estudiantes.xlsx'
    
    cargar_estudiantes_github(URL_GITHUB)