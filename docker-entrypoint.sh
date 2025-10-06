#!/bin/bash
"""
🚀 Docker Entry Point - Dropshipping Assistant
Script de entrada para contenedor de producción
"""

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando Dropshipping Assistant...${NC}"

# Función para logging
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar variables de entorno críticas
check_env_vars() {
    log_info "Verificando variables de entorno..."
    
    required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            log_error "Variable de entorno requerida no configurada: $var"
            exit 1
        fi
    done
    
    log_info "Variables de entorno verificadas ✅"
}

# Esperar a que la base de datos esté disponible
wait_for_db() {
    log_info "Esperando a que la base de datos esté disponible..."
    
    while ! python manage.py check --database default >/dev/null 2>&1; do
        log_warning "Base de datos no disponible, esperando 5 segundos..."
        sleep 5
    done
    
    log_info "Base de datos disponible ✅"
}

# Esperar a Redis (para workers de Celery)
wait_for_redis() {
    log_info "Esperando a que Redis esté disponible..."
    
    while ! python -c "
import redis
import os
redis_url = os.environ.get('REDIS_URL', 'redis://redis:6379/1')
try:
    r = redis.from_url(redis_url)
    r.ping()
    print('Redis OK')
except:
    exit(1)
" >/dev/null 2>&1; do
        log_warning "Redis no disponible, esperando 5 segundos..."
        sleep 5
    done
    
    log_info "Redis disponible ✅"
}

# Ejecutar migraciones de base de datos
run_migrations() {
    log_info "Ejecutando migraciones de base de datos..."
    python manage.py migrate --noinput
    log_info "Migraciones completadas ✅"
}

# Recopilar archivos estáticos
collect_static() {
    log_info "Recopilando archivos estáticos..."
    python manage.py collectstatic --noinput --clear
    log_info "Archivos estáticos recopilados ✅"
}

# Crear superusuario si no existe
create_superuser() {
    log_info "Verificando superusuario..."
    
    if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ]; then
        python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$DJANGO_SUPERUSER_USERNAME').exists():
    User.objects.create_superuser('$DJANGO_SUPERUSER_USERNAME', '$DJANGO_SUPERUSER_EMAIL', '$DJANGO_SUPERUSER_PASSWORD')
    print('Superusuario creado: $DJANGO_SUPERUSER_USERNAME')
else:
    print('Superusuario ya existe: $DJANGO_SUPERUSER_USERNAME')
EOF
        log_info "Superusuario configurado ✅"
    else
        log_warning "Variables de superusuario no configuradas (DJANGO_SUPERUSER_*)"
    fi
}

# Configurar cron jobs si están habilitados
setup_cron() {
    if [ "$ENABLE_CRON" = "true" ]; then
        log_info "Configurando tareas programadas..."
        python manage.py crontab add
        log_info "Cron jobs configurados ✅"
    fi
}

# Función principal de inicialización
initialize() {
    log_info "=== INICIALIZANDO APLICACIÓN ==="
    
    check_env_vars
    wait_for_db
    run_migrations
    collect_static
    create_superuser
    setup_cron
    
    log_info "=== INICIALIZACIÓN COMPLETADA ==="
}

# Inicialización ligera para workers
initialize_worker() {
    log_info "=== INICIALIZANDO WORKER ==="
    
    check_env_vars
    wait_for_redis
    wait_for_db  # También necesita DB para almacenar resultados de jobs
    
    log_info "=== WORKER LISTO ==="
}

# Manejo de señales para shutdown graceful
cleanup() {
    log_info "Recibida señal de terminación, cerrando aplicación..."
    exit 0
}

trap cleanup SIGTERM SIGINT

# Verificar argumentos
if [ "$1" = "initialize" ]; then
    initialize
    exit 0
elif [ "$1" = "worker" ]; then
    initialize_worker
    shift
    exec "$@"
elif [ "$1" = "migrate" ]; then
    wait_for_db
    run_migrations
    exit 0
elif [ "$1" = "shell" ]; then
    wait_for_db
    python manage.py shell
    exit 0
elif [ "$1" = "bash" ]; then
    /bin/bash
    exit 0
fi

# Ejecutar inicialización completa antes de iniciar la aplicación
initialize

# Mostrar información del sistema
log_info "Python version: $(python --version)"
log_info "Django version: $(python -c 'import django; print(django.get_version())')"
log_info "Workers: ${GUNICORN_WORKERS:-3}"
log_info "Environment: ${DJANGO_ENV:-production}"

log_info "🌟 Iniciando servidor de aplicación..."

# Ejecutar comando principal
exec "$@"