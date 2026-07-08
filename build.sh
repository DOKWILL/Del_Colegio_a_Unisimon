#!/usr/bin/env bash
# Script de despliegue para Render.com
# Del Colegio a Unisimón — Universidad Simón Bolívar

set -o errexit  # Detener si hay error

echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "🗄️ Aplicando migraciones..."
python manage.py migrate

echo "✅ Build completado exitosamente."
