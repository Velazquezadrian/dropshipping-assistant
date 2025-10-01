# 🪟 Utilidades PowerShell para Dropshipping Assistant
# Archivo: utils.ps1
# Uso: .\utils.ps1 [comando]

param(
    [Parameter(Mandatory=$false)]
    [string]$Command = "help"
)

# Función para imprimir mensajes con colores
function Write-ColorOutput($ForegroundColor) {
    $fc = $host.UI.RawUI.ForegroundColor
    $host.UI.RawUI.ForegroundColor = $ForegroundColor
    if ($args) {
        Write-Output $args
    } else {
        $input | Write-Output
    }
    $host.UI.RawUI.ForegroundColor = $fc
}

function Write-Info($message) {
    Write-ColorOutput Blue "[INFO] $message"
}

function Write-Success($message) {
    Write-ColorOutput Green "[SUCCESS] $message"
}

function Write-Warning($message) {
    Write-ColorOutput Yellow "[WARNING] $message"
}

function Write-Error($message) {
    Write-ColorOutput Red "[ERROR] $message"
}

# Función para verificar si Docker está instalado
function Test-Docker {
    try {
        docker --version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Función para verificar si Docker Compose está instalado
function Test-DockerCompose {
    try {
        docker-compose --version | Out-Null
        return $true
    } catch {
        return $false
    }
}

# Función para inicializar el proyecto
function Initialize-Project {
    Write-Info "🚀 Inicializando proyecto..."
    
    # Verificar Docker
    if (-not (Test-Docker)) {
        Write-Error "Docker no está instalado. Por favor instala Docker Desktop primero."
        return
    }
    
    if (-not (Test-DockerCompose)) {
        Write-Error "Docker Compose no está disponible. Por favor actualiza Docker Desktop."
        return
    }
    
    # Crear archivo .env si no existe
    if (-not (Test-Path ".env")) {
        Write-Warning "Archivo .env no encontrado. Copiando desde .env.example..."
        Copy-Item ".env.example" ".env"
        Write-Warning "⚠️ Por favor configura las variables en .env antes de continuar"
    }
    
    # Crear directorios necesarios
    Write-Info "📁 Creando directorios necesarios..."
    New-Item -ItemType Directory -Force -Path "data", "logs", "static", "media", "backups" | Out-Null
    
    Write-Success "✅ Proyecto inicializado correctamente"
}

# Función para construir y ejecutar el proyecto
function Start-Project {
    Write-Info "🏗️ Construyendo y ejecutando proyecto..."
    
    # Construir imagen
    docker-compose build
    
    # Ejecutar migraciones
    Write-Info "🗄️ Ejecutando migraciones..."
    docker-compose run --rm app python manage.py migrate
    
    # Crear superusuario si no existe
    Write-Info "👤 Verificando superusuario..."
    docker-compose run --rm app python manage.py shell -c @"
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superusuario creado: admin/admin123')
else:
    print('Superusuario ya existe')
"@
    
    # Recopilar archivos estáticos
    Write-Info "📦 Recopilando archivos estáticos..."
    docker-compose run --rm app python manage.py collectstatic --noinput
    
    # Iniciar servicios
    Write-Info "🚀 Iniciando servicios..."
    docker-compose up -d
    
    Write-Success "✅ Proyecto iniciado correctamente"
    Write-Info "🌐 Aplicación disponible en: http://localhost:8000"
    Write-Info "👤 Admin panel: http://localhost:8000/admin (admin/admin123)"
}

# Función para detener el proyecto
function Stop-Project {
    Write-Info "⏹️ Deteniendo servicios..."
    docker-compose down
    Write-Success "✅ Servicios detenidos"
}

# Función para mostrar logs
function Show-Logs {
    Write-Info "📋 Mostrando logs de la aplicación..."
    docker-compose logs -f app
}

# Función para mostrar estado
function Show-Status {
    Write-Info "📊 Estado de los contenedores:"
    docker-compose ps
    
    Write-Info "💻 Uso de recursos:"
    docker stats --no-stream
    
    # Verificar endpoint de salud
    Write-Info "🏥 Verificando salud de la aplicación..."
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health/" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "✅ Aplicación respondiendo correctamente"
        } else {
            Write-Warning "⚠️ Aplicación responde con código: $($response.StatusCode)"
        }
    } catch {
        Write-Error "❌ Aplicación no responde"
    }
}

# Función para hacer backup
function Backup-Data {
    Write-Info "💾 Creando backup..."
    
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupDir = "backups\$timestamp"
    
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    
    # Backup base de datos SQLite
    if (Test-Path "db.sqlite3") {
        Copy-Item "db.sqlite3" "$backupDir\"
        Write-Info "📁 Base de datos respaldada"
    }
    
    # Backup configuración
    if (Test-Path ".env") {
        Copy-Item ".env" "$backupDir\"
        Write-Info "⚙️ Configuración respaldada"
    }
    
    # Backup logs
    Get-ChildItem -Path "." -Filter "*.log" | Copy-Item -Destination $backupDir
    
    # Comprimir backup
    $backupZip = "$backupDir.zip"
    Compress-Archive -Path $backupDir -DestinationPath $backupZip
    Remove-Item -Recurse -Force $backupDir
    
    Write-Success "✅ Backup completado: $backupZip"
}

# Función para limpiar el sistema
function Clean-System {
    Write-Info "🧹 Limpiando sistema..."
    
    # Limpiar contenedores parados
    docker container prune -f
    
    # Limpiar imágenes no utilizadas
    docker image prune -f
    
    # Limpiar volúmenes no utilizados
    docker volume prune -f
    
    # Limpiar archivos temporales de Python
    Get-ChildItem -Recurse -Name "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Name "__pycache__" -Directory | Remove-Item -Recurse -Force
    
    Write-Success "✅ Limpieza completada"
}

# Función para acceder al shell de la aplicación
function Enter-AppShell {
    Write-Info "🐚 Accediendo al shell de la aplicación..."
    docker-compose exec app bash
}

# Función para acceder al shell de Django
function Enter-DjangoShell {
    Write-Info "🐍 Accediendo al shell de Django..."
    docker-compose exec app python manage.py shell
}

# Función para ejecutar tests
function Run-Tests {
    Write-Info "🧪 Ejecutando tests..."
    docker-compose exec app python manage.py test
}

# Función para ejecutar scraping manual
function Run-Scraping {
    Write-Info "🕷️ Ejecutando scraping manual..."
    docker-compose exec app python manage.py scrape_products
}

# Función para mostrar ayuda
function Show-Help {
    Write-Info "🪟 Utilidades PowerShell - Dropshipping Assistant"
    Write-Output ""
    Write-Output "Comandos disponibles:"
    Write-Output "  init       - Inicializar proyecto (crear directorios, .env)"
    Write-Output "  start      - Construir y ejecutar proyecto"
    Write-Output "  stop       - Detener servicios"
    Write-Output "  status     - Mostrar estado y salud del sistema"
    Write-Output "  logs       - Mostrar logs de la aplicación"
    Write-Output "  backup     - Crear backup de datos"
    Write-Output "  clean      - Limpiar sistema (contenedores, imágenes)"
    Write-Output "  shell      - Acceder al shell de la aplicación"
    Write-Output "  django     - Acceder al shell de Django"
    Write-Output "  test       - Ejecutar tests"
    Write-Output "  scrape     - Ejecutar scraping manual"
    Write-Output "  help       - Mostrar esta ayuda"
    Write-Output ""
    Write-Output "Uso: .\utils.ps1 [comando]"
    Write-Output "Ejemplo: .\utils.ps1 start"
}

# Procesamiento del comando
switch ($Command.ToLower()) {
    "init" { Initialize-Project }
    "start" { Start-Project }
    "stop" { Stop-Project }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "backup" { Backup-Data }
    "clean" { Clean-System }
    "shell" { Enter-AppShell }
    "django" { Enter-DjangoShell }
    "test" { Run-Tests }
    "scrape" { Run-Scraping }
    "help" { Show-Help }
    default { 
        Write-Error "Comando no reconocido: $Command"
        Show-Help 
    }
}

# Ejemplos de uso adicionales:
<#
# Configurar ejecución de scripts (ejecutar como administrador)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Crear alias permanentes (agregar al perfil de PowerShell)
$profilePath = $PROFILE
if (!(Test-Path $profilePath)) {
    New-Item -ItemType File -Path $profilePath -Force
}

Add-Content $profilePath @'
# Alias para Dropshipping Assistant
function ds { .\utils.ps1 $args }
function ds-start { .\utils.ps1 start }
function ds-stop { .\utils.ps1 stop }
function ds-status { .\utils.ps1 status }
function ds-logs { .\utils.ps1 logs }
'@

# Después de agregar al perfil, reiniciar PowerShell y usar:
# ds start
# ds-status
# ds-logs
#>