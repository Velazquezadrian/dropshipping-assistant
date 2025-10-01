#!/usr/bin/env python3
"""
🔍 Sistema de Monitoreo de Producción
Monitorea el estado del sistema de dropshipping en producción
"""

import os
import sys
import time
import requests
import subprocess
import psutil
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('monitor')

class ProductionMonitor:
    """Monitor de producción para el sistema de dropshipping"""
    
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.ssl_url = "https://localhost"
        self.endpoints = [
            "/health",
            "/api/products/",
            "/admin/"
        ]
        
    def check_system_resources(self):
        """Verificar recursos del sistema"""
        logger.info("🖥️ Verificando recursos del sistema...")
        
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        logger.info(f"CPU: {cpu_percent}%")
        
        # Memoria
        memory = psutil.virtual_memory()
        logger.info(f"Memoria: {memory.percent}% (Usado: {memory.used // 1024 // 1024}MB)")
        
        # Disco
        disk = psutil.disk_usage('/')
        logger.info(f"Disco: {disk.percent}% (Libre: {disk.free // 1024 // 1024 // 1024}GB)")
        
        # Alertas
        if cpu_percent > 80:
            logger.warning(f"⚠️ CPU alta: {cpu_percent}%")
        
        if memory.percent > 85:
            logger.warning(f"⚠️ Memoria alta: {memory.percent}%")
        
        if disk.percent > 90:
            logger.warning(f"⚠️ Disco lleno: {disk.percent}%")
        
        return {
            'cpu': cpu_percent,
            'memory': memory.percent,
            'disk': disk.percent
        }
    
    def check_docker_containers(self):
        """Verificar estado de contenedores Docker"""
        logger.info("🐳 Verificando contenedores Docker...")
        
        try:
            # Obtener estado de contenedores
            result = subprocess.run(
                ["docker-compose", "ps", "--format", "json"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                logger.info("✅ Contenedores Docker operativos")
                return True
            else:
                logger.error(f"❌ Error en contenedores: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando Docker: {e}")
            return False
    
    def check_endpoints(self):
        """Verificar endpoints de la aplicación"""
        logger.info("🌐 Verificando endpoints...")
        
        results = {}
        
        for endpoint in self.endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ {endpoint}: OK ({response.status_code})")
                    results[endpoint] = True
                else:
                    logger.warning(f"⚠️ {endpoint}: {response.status_code}")
                    results[endpoint] = False
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ {endpoint}: Error - {e}")
                results[endpoint] = False
        
        return results
    
    def check_database(self):
        """Verificar conectividad con la base de datos"""
        logger.info("🗄️ Verificando base de datos...")
        
        try:
            # Usar comando Docker para verificar PostgreSQL
            result = subprocess.run([
                "docker-compose", "exec", "-T", "db", 
                "pg_isready", "-U", "dropship_user"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Base de datos conectada")
                return True
            else:
                logger.error("❌ Base de datos no disponible")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error verificando base de datos: {e}")
            return False
    
    def check_ssl_certificates(self):
        """Verificar certificados SSL"""
        logger.info("🔐 Verificando certificados SSL...")
        
        cert_files = [
            'certs/nginx-selfsigned.crt',
            'certs/nginx-selfsigned.key'
        ]
        
        all_exist = True
        for cert_file in cert_files:
            if os.path.exists(cert_file):
                logger.info(f"✅ {cert_file}: Presente")
            else:
                logger.warning(f"⚠️ {cert_file}: No encontrado")
                all_exist = False
        
        return all_exist
    
    def check_logs_for_errors(self):
        """Buscar errores en los logs"""
        logger.info("📋 Revisando logs de errores...")
        
        log_files = [
            'logs/dropship_bot.log',
            'logs/django.log'
        ]
        
        error_count = 0
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        recent_lines = lines[-100:]  # Últimas 100 líneas
                        
                        for line in recent_lines:
                            if 'ERROR' in line or 'CRITICAL' in line:
                                error_count += 1
                                logger.warning(f"⚠️ Error encontrado en {log_file}: {line.strip()}")
                                
                except Exception as e:
                    logger.error(f"❌ Error leyendo {log_file}: {e}")
        
        logger.info(f"📊 Errores encontrados en logs: {error_count}")
        return error_count
    
    def run_full_check(self):
        """Ejecutar verificación completa del sistema"""
        logger.info("🚀 INICIANDO MONITOREO COMPLETO DEL SISTEMA")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Resultados
        results = {
            'timestamp': start_time.isoformat(),
            'system_resources': self.check_system_resources(),
            'docker_containers': self.check_docker_containers(),
            'endpoints': self.check_endpoints(),
            'database': self.check_database(),
            'ssl_certificates': self.check_ssl_certificates(),
            'error_count': self.check_logs_for_errors()
        }
        
        # Resumen
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DEL MONITOREO")
        logger.info("=" * 60)
        
        # Estado general
        healthy_endpoints = sum(results['endpoints'].values())
        total_endpoints = len(results['endpoints'])
        
        if (results['docker_containers'] and 
            results['database'] and 
            healthy_endpoints == total_endpoints and
            results['error_count'] < 10):
            logger.info("🟢 Sistema SALUDABLE")
            status = "HEALTHY"
        elif (results['docker_containers'] and 
              results['database'] and 
              healthy_endpoints >= total_endpoints * 0.7):
            logger.warning("🟡 Sistema ESTABLE con advertencias")
            status = "WARNING"
        else:
            logger.error("🔴 Sistema CRÍTICO - Requiere atención")
            status = "CRITICAL"
        
        # Duración del monitoreo
        duration = datetime.now() - start_time
        logger.info(f"⏱️ Duración del monitoreo: {duration.total_seconds():.2f} segundos")
        
        results['status'] = status
        results['duration'] = duration.total_seconds()
        
        return results
    
    def continuous_monitoring(self, interval=300):
        """Monitoreo continuo cada X segundos"""
        logger.info(f"🔄 Iniciando monitoreo continuo (cada {interval} segundos)")
        
        while True:
            try:
                self.run_full_check()
                logger.info(f"😴 Esperando {interval} segundos...")
                time.sleep(interval)
            except KeyboardInterrupt:
                logger.info("⏹️ Monitoreo detenido por el usuario")
                break
            except Exception as e:
                logger.error(f"❌ Error en monitoreo continuo: {e}")
                time.sleep(30)  # Esperar menos tiempo en caso de error

def main():
    """Función principal"""
    monitor = ProductionMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Monitoreo continuo
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 300
        monitor.continuous_monitoring(interval)
    else:
        # Verificación única
        results = monitor.run_full_check()
        
        # Salir con código de error si el sistema no está saludable
        if results['status'] == "CRITICAL":
            sys.exit(1)
        elif results['status'] == "WARNING":
            sys.exit(2)
        else:
            sys.exit(0)

if __name__ == "__main__":
    main()