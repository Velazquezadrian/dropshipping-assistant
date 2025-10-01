"""
Comando para gestionar tareas cron
"""

from django.core.management.base import BaseCommand
from django.conf import settings
import subprocess
import sys


class Command(BaseCommand):
    help = 'Gestiona las tareas cron del dropship bot'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'action',
            choices=['add', 'show', 'remove', 'test'],
            help='Acción a realizar con las tareas cron'
        )
    
    def handle(self, *args, **options):
        action = options['action']
        
        if action == 'add':
            self.add_cron_jobs()
        elif action == 'show':
            self.show_cron_jobs()
        elif action == 'remove':
            self.remove_cron_jobs()
        elif action == 'test':
            self.test_cron_functions()
    
    def add_cron_jobs(self):
        """Agregar trabajos cron al sistema"""
        try:
            from django_crontab.management.commands.crontab import Command as CrontabCommand
            crontab_cmd = CrontabCommand()
            crontab_cmd.handle(action='add')
            self.stdout.write(
                self.style.SUCCESS('Trabajos cron agregados exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error agregando trabajos cron: {e}')
            )
    
    def show_cron_jobs(self):
        """Mostrar trabajos cron actuales"""
        try:
            from django_crontab.management.commands.crontab import Command as CrontabCommand
            crontab_cmd = CrontabCommand()
            crontab_cmd.handle(action='show')
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error mostrando trabajos cron: {e}')
            )
    
    def remove_cron_jobs(self):
        """Remover trabajos cron del sistema"""
        try:
            from django_crontab.management.commands.crontab import Command as CrontabCommand
            crontab_cmd = CrontabCommand()
            crontab_cmd.handle(action='remove')
            self.stdout.write(
                self.style.SUCCESS('Trabajos cron removidos exitosamente')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error removiendo trabajos cron: {e}')
            )
    
    def test_cron_functions(self):
        """Probar las funciones cron manualmente"""
        self.stdout.write('Probando funciones cron...')
        
        try:
            # Probar scraping
            self.stdout.write('1. Probando scraping...')
            from products.cron import scrape_products
            result = scrape_products()
            self.stdout.write(f'   Resultado: {result}')
            
            # Probar health check
            self.stdout.write('2. Probando health check...')
            from products.cron import health_check_cron
            result = health_check_cron()
            self.stdout.write(f'   Resultado: {result}')
            
            self.stdout.write(
                self.style.SUCCESS('Todas las funciones cron funcionan correctamente')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error probando funciones cron: {e}')
            )