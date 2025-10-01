#!/usr/bin/env python3
"""
💾 Sistema de Backup Automático
Realiza backups de la base de datos y archivos importantes
"""

import os
import sys
import subprocess
import tarfile
import gzip
import shutil
from datetime import datetime, timedelta
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('backup')

class BackupManager:
    """Gestor de backups para el sistema de producción"""
    
    def __init__(self):
        self.backup_dir = "backups"
        self.database_name = "dropship_prod"
        self.database_user = "usuario_prod"
        self.max_backups = 30  # Mantener últimos 30 backups
        
        # Crear directorio de backups
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def create_database_backup(self):
        """Crear backup de la base de datos PostgreSQL"""
        logger.info("🗄️ Creando backup de la base de datos...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"db_backup_{timestamp}.sql"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        try:
            # Comando para hacer dump de PostgreSQL usando Docker
            cmd = [
                "docker-compose", "exec", "-T", "db",
                "pg_dump", "-U", self.database_user, "-d", self.database_name
            ]
            
            # Ejecutar comando y guardar output
            with open(backup_path, 'w') as backup_file:
                result = subprocess.run(cmd, stdout=backup_file, stderr=subprocess.PIPE, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Backup de DB creado: {backup_filename}")
                
                # Comprimir el backup
                compressed_path = f"{backup_path}.gz"
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # Eliminar archivo sin comprimir
                os.remove(backup_path)
                logger.info(f"✅ Backup comprimido: {backup_filename}.gz")
                
                return compressed_path
            else:
                logger.error(f"❌ Error en backup de DB: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Excepción en backup de DB: {e}")
            return None
    
    def create_files_backup(self):
        """Crear backup de archivos importantes del sistema"""
        logger.info("📁 Creando backup de archivos del sistema...")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"files_backup_{timestamp}.tar.gz"
        backup_path = os.path.join(self.backup_dir, backup_filename)
        
        # Archivos y directorios importantes a respaldar
        important_paths = [
            '.env.production',
            'dropship_bot/settings.py',
            'docker-compose.yml',
            'docker-compose.prod.yml',
            'nginx.conf',
            'logs/',
            'media/',
            'static/',
            'certs/'
        ]
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                for path in important_paths:
                    if os.path.exists(path):
                        tar.add(path)
                        logger.info(f"📦 Agregado al backup: {path}")
                    else:
                        logger.warning(f"⚠️ Archivo no encontrado: {path}")
            
            logger.info(f"✅ Backup de archivos creado: {backup_filename}")
            return backup_path
            
        except Exception as e:
            logger.error(f"❌ Error en backup de archivos: {e}")
            return None
    
    def cleanup_old_backups(self):
        """Limpiar backups antiguos"""
        logger.info("🧹 Limpiando backups antiguos...")
        
        try:
            # Obtener lista de archivos de backup
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith(('.sql.gz', '.tar.gz')):
                    filepath = os.path.join(self.backup_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    backup_files.append((filepath, mtime))
            
            # Ordenar por fecha (más antiguos primero)
            backup_files.sort(key=lambda x: x[1])
            
            # Eliminar backups antiguos si exceden el máximo
            if len(backup_files) > self.max_backups:
                files_to_delete = backup_files[:-self.max_backups]
                for filepath, _ in files_to_delete:
                    os.remove(filepath)
                    logger.info(f"🗑️ Backup antiguo eliminado: {os.path.basename(filepath)}")
            
            logger.info(f"✅ Cleanup completado. Backups mantenidos: {min(len(backup_files), self.max_backups)}")
            
        except Exception as e:
            logger.error(f"❌ Error en cleanup: {e}")
    
    def create_full_backup(self):
        """Crear backup completo del sistema"""
        logger.info("🚀 INICIANDO BACKUP COMPLETO DEL SISTEMA")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # Backup de base de datos
        db_backup = self.create_database_backup()
        
        # Backup de archivos
        files_backup = self.create_files_backup()
        
        # Cleanup de backups antiguos
        self.cleanup_old_backups()
        
        # Resumen
        duration = datetime.now() - start_time
        logger.info("=" * 60)
        logger.info("📊 RESUMEN DEL BACKUP")
        logger.info("=" * 60)
        logger.info(f"⏱️ Duración: {duration.total_seconds():.2f} segundos")
        
        if db_backup and files_backup:
            logger.info("🟢 Backup COMPLETADO exitosamente")
            
            # Calcular tamaños
            db_size = os.path.getsize(db_backup) / 1024 / 1024  # MB
            files_size = os.path.getsize(files_backup) / 1024 / 1024  # MB
            
            logger.info(f"📦 Backup de DB: {os.path.basename(db_backup)} ({db_size:.2f} MB)")
            logger.info(f"📦 Backup de archivos: {os.path.basename(files_backup)} ({files_size:.2f} MB)")
            
            return True
        else:
            logger.error("🔴 Backup FALLÓ")
            return False
    
    def restore_database(self, backup_file):
        """Restaurar base de datos desde backup"""
        logger.info(f"🔄 Restaurando base de datos desde: {backup_file}")
        
        if not os.path.exists(backup_file):
            logger.error(f"❌ Archivo de backup no encontrado: {backup_file}")
            return False
        
        try:
            # Descomprimir si es necesario
            if backup_file.endswith('.gz'):
                temp_file = backup_file[:-3]  # Remover .gz
                with gzip.open(backup_file, 'rb') as f_in:
                    with open(temp_file, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                sql_file = temp_file
            else:
                sql_file = backup_file
            
            # Restaurar usando Docker
            cmd = [
                "docker-compose", "exec", "-T", "db",
                "psql", "-U", self.database_user, "-d", self.database_name
            ]
            
            with open(sql_file, 'r') as backup_file:
                result = subprocess.run(cmd, stdin=backup_file, stderr=subprocess.PIPE, text=True)
            
            # Limpiar archivo temporal si se creó
            if sql_file != backup_file:
                os.remove(sql_file)
            
            if result.returncode == 0:
                logger.info("✅ Base de datos restaurada exitosamente")
                return True
            else:
                logger.error(f"❌ Error restaurando DB: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Excepción restaurando DB: {e}")
            return False
    
    def list_backups(self):
        """Listar backups disponibles"""
        logger.info("📋 Backups disponibles:")
        
        try:
            backup_files = []
            for filename in os.listdir(self.backup_dir):
                if filename.endswith(('.sql.gz', '.tar.gz')):
                    filepath = os.path.join(self.backup_dir, filename)
                    size = os.path.getsize(filepath) / 1024 / 1024  # MB
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    backup_files.append((filename, size, mtime))
            
            # Ordenar por fecha (más recientes primero)
            backup_files.sort(key=lambda x: x[2], reverse=True)
            
            for filename, size, mtime in backup_files:
                logger.info(f"  📦 {filename} - {size:.2f}MB - {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return backup_files
            
        except Exception as e:
            logger.error(f"❌ Error listando backups: {e}")
            return []

def main():
    """Función principal"""
    backup_manager = BackupManager()
    
    if len(sys.argv) < 2:
        print("Uso: python backup_production.py [comando]")
        print("Comandos:")
        print("  backup    - Crear backup completo")
        print("  list      - Listar backups disponibles")
        print("  restore   - Restaurar desde backup (requiere archivo)")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "backup":
        success = backup_manager.create_full_backup()
        sys.exit(0 if success else 1)
        
    elif command == "list":
        backup_manager.list_backups()
        
    elif command == "restore":
        if len(sys.argv) < 3:
            print("Error: Especifica el archivo de backup para restaurar")
            sys.exit(1)
        backup_file = sys.argv[2]
        success = backup_manager.restore_database(backup_file)
        sys.exit(0 if success else 1)
        
    else:
        print(f"Comando no reconocido: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()