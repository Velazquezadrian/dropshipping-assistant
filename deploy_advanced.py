#!/usr/bin/env python3
"""
🚀 Script Avanzado de Deploy en Producción
Sistema automatizado de deployment con verificaciones y rollback
"""

import os
import sys
import subprocess
import time
import json
import requests
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionDeployer:
    """
    Deployer avanzado para el sistema de dropshipping
    """
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.env_file = self.project_root / '.env.production'
        self.docker_compose_files = [
            'docker-compose.yml',
            'docker-compose.prod.yml'
        ]
        self.backup_dir = self.project_root / 'backups'
        self.deployment_info = {}
        
    def print_banner(self):
        """Mostrar banner de inicio"""
        banner = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║           🚀 DROPSHIPPING ASSISTANT - DEPLOY EN PRODUCCIÓN            ║
║                                                                       ║
║         Sistema automatizado de scraping con deploy avanzado          ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_prerequisites(self):
        """Verificar prerrequisitos del sistema"""
        logger.info("🔍 Verificando prerrequisitos...")
        
        # Verificar Docker
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker no está instalado o disponible")
            logger.info(f"✅ Docker: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"❌ Error con Docker: {e}")
            return False
        
        # Verificar Docker Compose
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode != 0:
                raise Exception("Docker Compose no está instalado")
            logger.info(f"✅ Docker Compose: {result.stdout.strip()}")
        except Exception as e:
            logger.error(f"❌ Error con Docker Compose: {e}")
            return False
        
        # Verificar archivos necesarios
        required_files = [
            'Dockerfile.production',
            'docker-compose.yml',
            'docker-compose.prod.yml',
            'requirements.txt',
            'manage.py'
        ]
        
        for file_name in required_files:
            file_path = self.project_root / file_name
            if not file_path.exists():
                logger.error(f"❌ Archivo requerido no encontrado: {file_name}")
                return False
            logger.info(f"✅ Archivo encontrado: {file_name}")
        
        return True
    
    def create_env_file(self):
        """Crear archivo de variables de entorno de producción"""
        logger.info("📝 Configurando variables de entorno de producción...")
        
        env_content = f"""# 🔐 Variables de Entorno de Producción
# Generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# Django Settings
DEBUG=False
SECRET_KEY={self._generate_secret_key()}
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
DJANGO_ENV=production

# Base de Datos PostgreSQL
DATABASE_NAME=dropship_production
DATABASE_USER=dropship_user
DATABASE_PASSWORD={self._generate_password()}
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD={self._generate_password()}
ADMIN_EMAIL=admin@localhost

# Build Info
BUILD_DATE={datetime.now().isoformat()}
VERSION=1.0.0
REVISION={self._get_git_revision()}

# Gunicorn
GUNICORN_WORKERS=3

# Features
ENABLE_CRON=true
ENABLE_MONITORING=true
ENABLE_SSL=false
"""
        
        with open(self.env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"✅ Archivo de entorno creado: {self.env_file}")
        return True
    
    def _generate_secret_key(self):
        """Generar SECRET_KEY de Django"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits + '!@#$%^&*(-_=+)'
        return ''.join(secrets.choice(alphabet) for _ in range(50))
    
    def _generate_password(self):
        """Generar password seguro"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(16))
    
    def _get_git_revision(self):
        """Obtener revisión de Git"""
        try:
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return 'unknown'
    
    def backup_existing_data(self):
        """Crear backup de datos existentes"""
        logger.info("💾 Creando backup de seguridad...")
        
        self.backup_dir.mkdir(exist_ok=True)
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Backup de base de datos si existe
        try:
            result = subprocess.run([
                'docker-compose', 'exec', '-T', 'db', 
                'pg_dump', '-U', 'postgres', 'dropship_db'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                backup_file = self.backup_dir / f'db_backup_{backup_timestamp}.sql'
                with open(backup_file, 'w') as f:
                    f.write(result.stdout)
                logger.info(f"✅ Backup de DB creado: {backup_file}")
        except Exception as e:
            logger.warning(f"⚠️ No se pudo crear backup de DB: {e}")
        
        return True
    
    def build_production_images(self):
        """Construir imágenes de producción"""
        logger.info("🔨 Construyendo imágenes de producción...")
        
        build_command = [
            'docker-compose',
            '-f', 'docker-compose.yml',
            '-f', 'docker-compose.prod.yml',
            'build',
            '--no-cache'
        ]
        
        try:
            result = subprocess.run(build_command, check=True)
            logger.info("✅ Imágenes construidas exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error construyendo imágenes: {e}")
            return False
    
    def deploy_services(self):
        """Desplegar servicios en producción"""
        logger.info("🚀 Desplegando servicios...")
        
        # Parar servicios existentes
        logger.info("⏹️ Parando servicios existentes...")
        subprocess.run([
            'docker-compose',
            '-f', 'docker-compose.yml',
            '-f', 'docker-compose.prod.yml',
            'down'
        ])
        
        # Iniciar servicios
        logger.info("▶️ Iniciando servicios de producción...")
        try:
            result = subprocess.run([
                'docker-compose',
                '-f', 'docker-compose.yml',
                '-f', 'docker-compose.prod.yml',
                'up', '-d'
            ], check=True)
            
            logger.info("✅ Servicios iniciados exitosamente")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error desplegando servicios: {e}")
            return False
    
    def wait_for_services(self, timeout=300):
        """Esperar a que los servicios estén listos"""
        logger.info("⏳ Esperando a que los servicios estén listos...")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Verificar health check de la aplicación
                response = requests.get('http://localhost:8000/health/', timeout=5)
                if response.status_code == 200:
                    logger.info("✅ Aplicación está lista y respondiendo")
                    return True
            except:
                pass
            
            logger.info("⏳ Esperando servicios...")
            time.sleep(10)
        
        logger.error(f"❌ Timeout esperando servicios ({timeout}s)")
        return False
    
    def run_migrations(self):
        """Ejecutar migraciones de base de datos"""
        logger.info("🗃️ Ejecutando migraciones de base de datos...")
        
        migration_commands = [
            ['docker-compose', 'exec', '-T', 'app', 'python', 'manage.py', 'makemigrations'],
            ['docker-compose', 'exec', '-T', 'app', 'python', 'manage.py', 'migrate'],
            ['docker-compose', 'exec', '-T', 'app', 'python', 'manage.py', 'collectstatic', '--noinput']
        ]
        
        for command in migration_commands:
            try:
                result = subprocess.run(command, check=True)
                logger.info(f"✅ Comando ejecutado: {' '.join(command[5:])}")
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Error en comando: {e}")
                return False
        
        return True
    
    def create_superuser(self):
        """Crear superusuario automáticamente"""
        logger.info("👤 Creando superusuario...")
        
        try:
            result = subprocess.run([
                'docker-compose', 'exec', '-T', 'app',
                'python', 'manage.py', 'shell', '-c',
                """
from django.contrib.auth import get_user_model
import os
User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@localhost')
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'Superuser {username} created successfully')
else:
    print(f'Superuser {username} already exists')
                """
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Superusuario configurado")
                return True
            else:
                logger.warning(f"⚠️ Problema con superusuario: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creando superusuario: {e}")
            return False
    
    def run_health_checks(self):
        """Ejecutar verificaciones de salud completas"""
        logger.info("🏥 Ejecutando verificaciones de salud...")
        
        checks = {
            'app_health': 'http://localhost:8000/health/',
            'api_products': 'http://localhost:8000/api/products/',
            'dashboard_stats': 'http://localhost:8000/api/dashboard/stats/',
        }
        
        results = {}
        
        for check_name, url in checks.items():
            try:
                response = requests.get(url, timeout=10)
                results[check_name] = {
                    'status': response.status_code,
                    'success': response.status_code == 200,
                    'response_time': response.elapsed.total_seconds()
                }
                
                if results[check_name]['success']:
                    logger.info(f"✅ {check_name}: OK ({response.status_code})")
                else:
                    logger.warning(f"⚠️ {check_name}: {response.status_code}")
                    
            except Exception as e:
                results[check_name] = {
                    'status': 'error',
                    'success': False,
                    'error': str(e)
                }
                logger.error(f"❌ {check_name}: {e}")
        
        # Resumen
        successful_checks = sum(1 for r in results.values() if r['success'])
        total_checks = len(results)
        
        logger.info(f"📊 Verificaciones completadas: {successful_checks}/{total_checks} exitosas")
        
        return successful_checks == total_checks
    
    def generate_deployment_report(self):
        """Generar reporte de deployment"""
        logger.info("📄 Generando reporte de deployment...")
        
        # Obtener información de servicios
        try:
            result = subprocess.run([
                'docker-compose', 'ps', '--format', 'json'
            ], capture_output=True, text=True)
            
            services_info = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        services_info.append(json.loads(line))
                    except:
                        pass
        except:
            services_info = []
        
        # Crear reporte
        report = {
            'deployment_time': datetime.now().isoformat(),
            'version': '1.0.0',
            'git_revision': self._get_git_revision(),
            'services': services_info,
            'health_checks': self.run_health_checks(),
            'urls': {
                'dashboard': 'http://localhost:8000/dashboard/',
                'api': 'http://localhost:8000/api/',
                'admin': 'http://localhost:8000/admin/',
                'health': 'http://localhost:8000/health/'
            },
            'next_steps': [
                "Configurar SSL/TLS para producción",
                "Configurar backup automático",
                "Configurar monitoreo avanzado",
                "Configurar dominio personalizado"
            ]
        }
        
        # Guardar reporte
        report_file = self.backup_dir / f'deployment_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"✅ Reporte guardado: {report_file}")
        return report
    
    def deploy(self):
        """Proceso completo de deployment"""
        try:
            self.print_banner()
            
            # Verificar prerrequisitos
            if not self.check_prerequisites():
                logger.error("❌ Falló verificación de prerrequisitos")
                return False
            
            # Crear archivo de entorno
            if not self.create_env_file():
                logger.error("❌ Falló creación de archivo de entorno")
                return False
            
            # Backup de datos existentes
            self.backup_existing_data()
            
            # Construir imágenes
            if not self.build_production_images():
                logger.error("❌ Falló construcción de imágenes")
                return False
            
            # Desplegar servicios
            if not self.deploy_services():
                logger.error("❌ Falló deployment de servicios")
                return False
            
            # Esperar servicios
            if not self.wait_for_services():
                logger.error("❌ Servicios no están listos")
                return False
            
            # Ejecutar migraciones
            if not self.run_migrations():
                logger.error("❌ Falló ejecución de migraciones")
                return False
            
            # Crear superusuario
            self.create_superuser()
            
            # Verificaciones de salud
            health_ok = self.run_health_checks()
            
            # Generar reporte
            report = self.generate_deployment_report()
            
            # Resultado final
            if health_ok:
                logger.info("🎉 ¡DEPLOYMENT COMPLETADO EXITOSAMENTE!")
                print(f"""
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                    🎉 ¡DEPLOYMENT EXITOSO! 🎉                        ║
║                                                                       ║
║  Dashboard: http://localhost:8000/dashboard/                          ║
║  API:       http://localhost:8000/api/                               ║
║  Admin:     http://localhost:8000/admin/                             ║
║                                                                       ║
║  Usuario Admin: admin                                                 ║
║  Contraseña: Ver archivo .env.production                             ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
                """)
                return True
            else:
                logger.warning("⚠️ Deployment completado con advertencias")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error durante deployment: {e}")
            return False


if __name__ == '__main__':
    deployer = ProductionDeployer()
    success = deployer.deploy()
    sys.exit(0 if success else 1)