#!/bin/bash

# 🚀 Script de Despliegue Automatizado - Dropshipping Assistant
# Uso: ./deploy.sh [development|production]

set -e  # Salir si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes con colores
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar argumentos
ENVIRONMENT=${1:-development}

print_status "🚀 Iniciando despliegue en modo: $ENVIRONMENT"

# Verificar que Docker esté instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker no está instalado. Por favor instala Docker primero."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose no está instalado. Por favor instala Docker Compose primero."
    exit 1
fi

# Verificar que el archivo .env existe
if [ ! -f .env ]; then
    print_warning "Archivo .env no encontrado. Copiando desde .env.example..."
    cp .env.example .env
    print_warning "⚠️  Por favor configura las variables en .env antes de continuar"
    print_warning "⚠️  Especialmente: SECRET_KEY, TELEGRAM_BOT_TOKEN, DISCORD_WEBHOOK_URL"
    read -p "¿Has configurado el archivo .env? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Por favor configura .env y ejecuta el script nuevamente"
        exit 1
    fi
fi

# Crear directorios necesarios
print_status "📁 Creando directorios necesarios..."
mkdir -p data logs static media

# Función para despliegue en desarrollo
deploy_development() {
    print_status "🔧 Configurando entorno de desarrollo..."
    
    # Construir imagen
    print_status "🏗️  Construyendo imagen Docker..."
    docker-compose build
    
    # Ejecutar migraciones
    print_status "🗄️  Ejecutando migraciones de base de datos..."
    docker-compose run --rm app python manage.py migrate
    
    # Crear superusuario si no existe
    print_status "👤 Verificando superusuario..."
    docker-compose run --rm app python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"
    
    # Recopilar archivos estáticos
    print_status "📦 Recopilando archivos estáticos..."
    docker-compose run --rm app python manage.py collectstatic --noinput
    
    # Iniciar servicios
    print_status "🚀 Iniciando servicios..."
    docker-compose up -d
    
    print_success "✅ Despliegue de desarrollo completado"
    print_status "🌐 Aplicación disponible en: http://localhost:8000"
    print_status "👤 Admin panel: http://localhost:8000/admin (admin/admin123)"
    print_status "📚 API docs: http://localhost:8000/api/"
}

# Función para despliegue en producción
deploy_production() {
    print_status "🏭 Configurando entorno de producción..."
    
    # Verificar variables críticas
    if grep -q "django-insecure" .env; then
        print_error "❌ SECRET_KEY insegura detectada en .env"
        print_error "Por favor genera una SECRET_KEY segura para producción"
        exit 1
    fi
    
    # Construir imagen
    print_status "🏗️  Construyendo imagen Docker..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml build
    
    # Ejecutar migraciones
    print_status "🗄️  Ejecutando migraciones de base de datos..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm app python manage.py migrate
    
    # Recopilar archivos estáticos
    print_status "📦 Recopilando archivos estáticos..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm app python manage.py collectstatic --noinput
    
    # Crear superusuario si es necesario
    print_warning "⚠️  Recuerda crear un superusuario para producción"
    
    # Iniciar servicios
    print_status "🚀 Iniciando servicios en producción..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    print_success "✅ Despliegue de producción completado"
    print_status "🌐 Aplicación disponible en: http://localhost"
    print_warning "🔒 Configura HTTPS y dominio para producción real"
}

# Función para verificar el estado de los servicios
check_services() {
    print_status "🔍 Verificando estado de los servicios..."
    
    # Esperar a que los servicios estén listos
    sleep 10
    
    # Verificar que la aplicación responda
    if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
        print_success "✅ Aplicación respondiendo correctamente"
    else
        print_error "❌ La aplicación no responde en el endpoint de salud"
        print_status "📋 Logs de la aplicación:"
        docker-compose logs app --tail=20
    fi
    
    # Mostrar estado de los contenedores
    print_status "📊 Estado de los contenedores:"
    docker-compose ps
}

# Función principal
main() {
    case $ENVIRONMENT in
        development|dev)
            deploy_development
            ;;
        production|prod)
            deploy_production
            ;;
        *)
            print_error "Entorno no válido: $ENVIRONMENT"
            print_status "Uso: $0 [development|production]"
            exit 1
            ;;
    esac
    
    check_services
    
    print_success "🎉 ¡Despliegue completado exitosamente!"
    print_status "📝 Para ver los logs: docker-compose logs -f"
    print_status "⏹️  Para detener: docker-compose down"
    print_status "🔄 Para reiniciar: docker-compose restart"
}

# Ejecutar función principal
main