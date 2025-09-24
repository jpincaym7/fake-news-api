#!/usr/bin/env bash
# Script de construcción para despliegue en Render

set -o errexit  # Salir con error si cualquier comando falla

echo "🔨 Iniciando proceso de construcción..."

# Instalar dependencias de Python
echo "📦 Instalando dependencias..."
pip install -r requirements.txt

echo "🗄️ Configurando base de datos..."
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate

echo "🔧 Creando superusuario (si no existe)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('✅ Superusuario creado')
else:
    print('✅ Superusuario ya existe')
EOF

echo "🚀 Construcción completada exitosamente"