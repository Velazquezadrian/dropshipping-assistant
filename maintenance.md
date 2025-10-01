# 📊 Scripts de Monitoreo y Mantenimiento

# ===== SCRIPT DE MONITOREO BÁSICO =====
# Archivo: monitor.sh
#!/bin/bash

# 📊 Monitor del Sistema de Dropshipping
# Ejecutar: ./monitor.sh

echo "🔍 === MONITOREO DEL SISTEMA ==="
echo "📅 Fecha: $(date)"
echo ""

# Estado de contenedores
echo "🐳 === ESTADO DE CONTENEDORES ==="
docker-compose ps
echo ""

# Uso de recursos
echo "💻 === USO DE RECURSOS ==="
docker stats --no-stream
echo ""

# Logs recientes de la aplicación
echo "📝 === LOGS RECIENTES (últimas 10 líneas) ==="
docker-compose logs --tail=10 app
echo ""

# Verificar endpoint de salud
echo "🏥 === VERIFICACIÓN DE SALUD ==="
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    echo "✅ Aplicación respondiendo correctamente"
else
    echo "❌ Aplicación no responde"
fi
echo ""

# Espacio en disco
echo "💾 === ESPACIO EN DISCO ==="
df -h | grep -E "(Filesystem|/dev/)"
echo ""

# Procesos de Python
echo "🐍 === PROCESOS PYTHON ==="
ps aux | grep python | grep -v grep
echo ""

echo "🔍 === MONITOREO COMPLETADO ==="

# ===== SCRIPT DE BACKUP =====
# Archivo: backup.sh
#!/bin/bash

echo "💾 === BACKUP DEL SISTEMA ==="

# Crear directorio de backup con timestamp
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# Backup de la base de datos SQLite
echo "📁 Respaldando base de datos..."
cp db.sqlite3 "$BACKUP_DIR/" 2>/dev/null || echo "⚠️ No se encontró db.sqlite3"

# Backup de configuración
echo "⚙️ Respaldando configuración..."
cp .env "$BACKUP_DIR/" 2>/dev/null || echo "⚠️ No se encontró .env"

# Backup de logs
echo "📋 Respaldando logs..."
cp *.log "$BACKUP_DIR/" 2>/dev/null || echo "ℹ️ No hay archivos de log"

# Backup usando Docker (PostgreSQL)
echo "🗄️ Respaldando PostgreSQL..."
docker-compose exec -T db pg_dump -U ${DATABASE_USER:-postgres} ${DATABASE_NAME:-dropship_bot} > "$BACKUP_DIR/postgres_backup.sql" 2>/dev/null || echo "⚠️ No se pudo respaldar PostgreSQL"

# Comprimir backup
echo "🗜️ Comprimiendo backup..."
tar -czf "${BACKUP_DIR}.tar.gz" -C backups "$(basename $BACKUP_DIR)"
rm -rf "$BACKUP_DIR"

echo "✅ Backup completado: ${BACKUP_DIR}.tar.gz"

# ===== SCRIPT DE LIMPIEZA =====
# Archivo: cleanup.sh
#!/bin/bash

echo "🧹 === LIMPIEZA DEL SISTEMA ==="

# Limpiar contenedores parados
echo "🐳 Limpiando contenedores parados..."
docker container prune -f

# Limpiar imágenes no utilizadas
echo "📦 Limpiando imágenes no utilizadas..."
docker image prune -f

# Limpiar volúmenes no utilizados
echo "💾 Limpiando volúmenes no utilizados..."
docker volume prune -f

# Limpiar redes no utilizadas
echo "🌐 Limpiando redes no utilizadas..."
docker network prune -f

# Limpiar logs antiguos (más de 30 días)
echo "📋 Limpiando logs antiguos..."
find . -name "*.log" -type f -mtime +30 -delete 2>/dev/null || echo "ℹ️ No hay logs antiguos"

# Limpiar archivos temporales de Python
echo "🐍 Limpiando archivos temporales de Python..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

echo "✅ Limpieza completada"

# ===== SCRIPT DE ACTUALIZACIÓN =====
# Archivo: update.sh
#!/bin/bash

echo "🔄 === ACTUALIZACIÓN DEL SISTEMA ==="

# Hacer backup antes de actualizar
echo "💾 Creando backup antes de actualizar..."
./backup.sh

# Detener servicios
echo "⏹️ Deteniendo servicios..."
docker-compose down

# Actualizar código
echo "📥 Actualizando código..."
git pull origin main

# Reconstruir imágenes
echo "🏗️ Reconstruyendo imágenes..."
docker-compose build --no-cache

# Ejecutar migraciones
echo "🗄️ Ejecutando migraciones..."
docker-compose run --rm app python manage.py migrate

# Reiniciar servicios
echo "🚀 Reiniciando servicios..."
docker-compose up -d

echo "✅ Actualización completada"

# ===== COMANDOS DE CRON PARA AUTOMATIZACIÓN =====
# Agregar al crontab del sistema:

# Monitoreo cada 15 minutos
# */15 * * * * cd /ruta/a/dropshipping && ./monitor.sh >> logs/monitor.log 2>&1

# Backup diario a las 2:00 AM
# 0 2 * * * cd /ruta/a/dropshipping && ./backup.sh >> logs/backup.log 2>&1

# Limpieza semanal (domingos a las 3:00 AM)
# 0 3 * * 0 cd /ruta/a/dropshipping && ./cleanup.sh >> logs/cleanup.log 2>&1

# Reinicio semanal de servicios (lunes a las 4:00 AM)
# 0 4 * * 1 cd /ruta/a/dropshipping && docker-compose restart

# ===== ALERTAS DE MONITOREO =====
# Script: alert.sh
#!/bin/bash

# Verificar si la aplicación está respondiendo
if ! curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    # Enviar alerta por email (configurar sendmail o similar)
    echo "❌ ALERTA: Aplicación de dropshipping no responde" | mail -s "Alerta Sistema" admin@tudominio.com
    
    # Enviar notificación a Telegram
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d text="🚨 ALERTA: Sistema de dropshipping no responde en $(hostname) - $(date)"
fi

# Verificar uso de disco
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "⚠️ ALERTA: Uso de disco alto: ${DISK_USAGE}%" | mail -s "Alerta Disco" admin@tudominio.com
fi

# ===== GUÍA DE USO =====
# 1. Hacer los scripts ejecutables:
#    chmod +x monitor.sh backup.sh cleanup.sh update.sh alert.sh

# 2. Configurar cron jobs:
#    crontab -e
#    (agregar las líneas de cron mostradas arriba)

# 3. Configurar alertas:
#    - Instalar y configurar sendmail para emails
#    - Configurar variables TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID

# 4. Crear directorios necesarios:
#    mkdir -p backups logs

echo "📚 === GUÍA DE MANTENIMIENTO ==="
echo "🔍 Monitoreo:   ./monitor.sh"
echo "💾 Backup:      ./backup.sh"  
echo "🧹 Limpieza:    ./cleanup.sh"
echo "🔄 Actualizar:  ./update.sh"
echo "🚨 Alertas:     ./alert.sh"
echo ""
echo "📋 Ver logs:    docker-compose logs -f"
echo "📊 Estadísticas: docker stats"
echo "🔧 Shell app:   docker-compose exec app bash"
echo "🗄️ Shell DB:    docker-compose exec db psql -U postgres dropship_bot"