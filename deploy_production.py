#!/usr/bin/env python
"""
Script de despliegue en producción
Configura y despliega el sistema completo con Docker
"""
import os
import subprocess
import sys
import time

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - Completado")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - Error:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - Excepción: {e}")
        return False

def check_prerequisites():
    """Verificar prerrequisitos para despliegue"""
    print("🔍 Verificando prerrequisitos...")
    
    # Verificar Docker
    if not run_command("docker --version", "Verificar Docker"):
        print("❌ Docker no está instalado o no está funcionando")
        return False
    
    # Verificar Docker Compose
    if not run_command("docker-compose --version", "Verificar Docker Compose"):
        print("❌ Docker Compose no está disponible")
        return False
    
    # Verificar archivos necesarios
    required_files = [
        'docker-compose.yml',
        'docker-compose.prod.yml',
        'Dockerfile',
        'nginx.conf',
        '.env.production'
    ]
    
    for file in required_files:
        if not os.path.exists(file):
            print(f"❌ Archivo requerido no encontrado: {file}")
            return False
    
    print("✅ Todos los prerrequisitos están cumplidos")
    return True

def setup_environment():
    """Configurar entorno de producción"""
    print("\n📁 Configurando entorno de producción...")
    
    # Copiar configuración de producción
    if os.path.exists('.env.production'):
        if os.path.exists('.env'):
            # Hacer backup del .env actual
            run_command("copy .env .env.backup", "Respaldar configuración actual")
        
        run_command("copy .env.production .env", "Copiar configuración de producción")
        print("⚠️ IMPORTANTE: Revisa y configura las variables en .env antes de continuar")
        
        # Mostrar variables que necesitan configuración
        print("\n🔧 Variables que debes configurar:")
        print("- SECRET_KEY: Genera una clave segura")
        print("- TELEGRAM_BOT_TOKEN: Token real de tu bot")
        print("- TELEGRAM_CHAT_ID: Chat ID real")
        print("- DISCORD_WEBHOOK_URL: URL real del webhook")
        print("- DATABASE_PASSWORD: Contraseña segura para PostgreSQL")
        print("- ALLOWED_HOSTS: Tu dominio real")
        
        return True
    else:
        print("❌ Archivo .env.production no encontrado")
        return False

def generate_certificates():
    """Generar certificados SSL para desarrollo/testing"""
    print("\n🔐 Configurando certificados SSL...")
    
    # Crear directorio de certificados
    os.makedirs('certs', exist_ok=True)
    
    # Para Windows, crear certificados auto-firmados básicos
    # Nota: En producción real, usar Let's Encrypt
    
    print("ℹ️ Para producción, configura certificados reales:")
    print("1. Usa Let's Encrypt para certificados gratuitos")
    print("2. O coloca tus certificados en el directorio certs/")
    print("   - nginx-selfsigned.crt")
    print("   - nginx-selfsigned.key")
    
    return True

def deploy_production():
    """Desplegar en modo producción"""
    print("\n🚀 Desplegando en producción...")
    
    # Construir imágenes
    if not run_command(
        "docker-compose -f docker-compose.yml -f docker-compose.prod.yml build", 
        "Construir imágenes Docker"
    ):
        return False
    
    # Ejecutar migraciones
    if not run_command(
        "docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm app python manage.py migrate", 
        "Ejecutar migraciones de base de datos"
    ):
        return False
    
    # Recopilar archivos estáticos
    if not run_command(
        "docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm app python manage.py collectstatic --noinput", 
        "Recopilar archivos estáticos"
    ):
        return False
    
    # Iniciar servicios
    if not run_command(
        "docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d", 
        "Iniciar servicios en producción"
    ):
        return False
    
    print("✅ Despliegue completado")
    return True

def verify_deployment():
    """Verificar que el despliegue funcione"""
    print("\n🔍 Verificando despliegue...")
    
    # Esperar a que los servicios se inicien
    print("⏳ Esperando que los servicios se inicien...")
    time.sleep(30)
    
    # Verificar estado de contenedores
    run_command("docker-compose ps", "Estado de contenedores")
    
    # Verificar logs de la aplicación
    print("\n📋 Logs de la aplicación (últimas 10 líneas):")
    run_command("docker-compose logs --tail=10 app", "Logs de aplicación")
    
    print("\n🌐 URLs disponibles:")
    print("- HTTP: http://localhost")
    print("- HTTPS: https://localhost")
    print("- Admin: https://localhost/admin")
    print("- API: https://localhost/api/")
    
    return True

def main():
    """Función principal"""
    print("🏭 === DESPLIEGUE EN PRODUCCIÓN ===")
    print("Sistema de Dropshipping Assistant")
    print("=" * 50)
    
    # Verificar prerrequisitos
    if not check_prerequisites():
        print("❌ Faltan prerrequisitos. Abortando despliegue.")
        return False
    
    # Configurar entorno
    if not setup_environment():
        print("❌ Error configurando entorno. Abortando.")
        return False
    
    # Preguntar confirmación
    print("\n⚠️ Este script configurará el sistema en modo PRODUCCIÓN")
    response = input("¿Continuar? (s/N): ").lower()
    if response != 's':
        print("Despliegue cancelado por el usuario")
        return False
    
    # Configurar certificados
    generate_certificates()
    
    # Desplegar
    if not deploy_production():
        print("❌ Error en el despliegue")
        return False
    
    # Verificar
    verify_deployment()
    
    print("\n🎉 ¡DESPLIEGUE COMPLETADO!")
    print("📝 Próximos pasos:")
    print("1. Configura tu dominio real")
    print("2. Instala certificados SSL reales")
    print("3. Configura tokens reales de Telegram/Discord")
    print("4. Configura monitoreo y backups automáticos")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)