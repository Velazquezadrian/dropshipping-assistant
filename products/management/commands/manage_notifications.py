"""
🔧 Comando Django para Gestión del Sistema de Notificaciones
Administrar filtros, plantillas y configuraciones avanzadas
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from products.models import Product
from products.services.notification_filters import (
    filter_engine, NotificationFilter, NotificationRule, FilterOperator, NotificationPriority
)
from products.services.notification_templates import (
    template_engine, NotificationTemplate, TemplateType
)
from products.services.notifications import notification_manager
import json


class Command(BaseCommand):
    """Comando para gestionar el sistema avanzado de notificaciones"""
    
    help = 'Gestionar filtros, plantillas y configuraciones del sistema de notificaciones'
    
    def add_arguments(self, parser):
        # Subcomandos principales
        subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
        
        # === FILTROS ===
        filters_parser = subparsers.add_parser('filters', help='Gestionar filtros de notificaciones')
        filters_subparsers = filters_parser.add_subparsers(dest='filter_action')
        
        # Listar filtros
        filters_subparsers.add_parser('list', help='Listar todas las reglas de filtros')
        
        # Agregar filtro
        add_filter = filters_subparsers.add_parser('add', help='Agregar nueva regla de filtro')
        add_filter.add_argument('--name', required=True, help='Nombre de la regla')
        add_filter.add_argument('--field', required=True, help='Campo a filtrar (price, rating, category, etc.)')
        add_filter.add_argument('--operator', required=True, choices=[op.value for op in FilterOperator], help='Operador de comparación')
        add_filter.add_argument('--value', required=True, help='Valor a comparar')
        add_filter.add_argument('--priority', choices=[p.value for p in NotificationPriority], default='normal', help='Prioridad de la regla')
        add_filter.add_argument('--template', default='default', help='Plantilla a usar')
        add_filter.add_argument('--platforms', nargs='+', default=['telegram', 'discord'], help='Plataformas habilitadas')
        
        # Eliminar filtro
        del_filter = filters_subparsers.add_parser('remove', help='Eliminar regla de filtro')
        del_filter.add_argument('name', help='Nombre de la regla a eliminar')
        
        # Habilitar/deshabilitar filtro
        toggle_filter = filters_subparsers.add_parser('toggle', help='Habilitar/deshabilitar regla de filtro')
        toggle_filter.add_argument('name', help='Nombre de la regla')
        toggle_filter.add_argument('--enable', action='store_true', help='Habilitar regla')
        toggle_filter.add_argument('--disable', action='store_true', help='Deshabilitar regla')
        
        # === PLANTILLAS ===
        templates_parser = subparsers.add_parser('templates', help='Gestionar plantillas de notificaciones')
        templates_subparsers = templates_parser.add_subparsers(dest='template_action')
        
        # Listar plantillas
        templates_subparsers.add_parser('list', help='Listar todas las plantillas')
        
        # Previsualizar plantilla
        preview_template = templates_subparsers.add_parser('preview', help='Previsualizar plantilla')
        preview_template.add_argument('name', help='Nombre de la plantilla')
        
        # Habilitar/deshabilitar plantilla
        toggle_template = templates_subparsers.add_parser('toggle', help='Habilitar/deshabilitar plantilla')
        toggle_template.add_argument('name', help='Nombre de la plantilla')
        toggle_template.add_argument('--enable', action='store_true', help='Habilitar plantilla')
        toggle_template.add_argument('--disable', action='store_true', help='Deshabilitar plantilla')
        
        # === ESTADÍSTICAS ===
        stats_parser = subparsers.add_parser('stats', help='Ver estadísticas del sistema')
        stats_parser.add_argument('--reset', action='store_true', help='Reiniciar estadísticas')
        
        # === PRUEBAS ===
        test_parser = subparsers.add_parser('test', help='Probar sistema de notificaciones')
        test_parser.add_argument('--product-id', type=int, help='ID de producto específico para probar')
        test_parser.add_argument('--all', action='store_true', help='Probar todos los servicios')
        
        # === CONFIGURACIÓN ===
        config_parser = subparsers.add_parser('config', help='Mostrar configuración del sistema')
    
    def handle(self, *args, **options):
        """Manejar comando principal"""
        command = options.get('command')
        
        if command == 'filters':
            self.handle_filters(options)
        elif command == 'templates':
            self.handle_templates(options)
        elif command == 'stats':
            self.handle_stats(options)
        elif command == 'test':
            self.handle_test(options)
        elif command == 'config':
            self.handle_config(options)
        else:
            self.print_help()
    
    def handle_filters(self, options):
        """Manejar comandos de filtros"""
        action = options.get('filter_action')
        
        if action == 'list':
            self.list_filters()
        elif action == 'add':
            self.add_filter(options)
        elif action == 'remove':
            self.remove_filter(options['name'])
        elif action == 'toggle':
            self.toggle_filter(options)
        else:
            self.stdout.write(self.style.ERROR('Acción de filtros no válida'))
    
    def handle_templates(self, options):
        """Manejar comandos de plantillas"""
        action = options.get('template_action')
        
        if action == 'list':
            self.list_templates()
        elif action == 'preview':
            self.preview_template(options['name'])
        elif action == 'toggle':
            self.toggle_template(options)
        else:
            self.stdout.write(self.style.ERROR('Acción de plantillas no válida'))
    
    def handle_stats(self, options):
        """Manejar comandos de estadísticas"""
        if options.get('reset'):
            notification_manager.reset_all_stats()
            self.stdout.write(self.style.SUCCESS('✅ Estadísticas reiniciadas'))
        else:
            self.show_stats()
    
    def handle_test(self, options):
        """Manejar comandos de prueba"""
        if options.get('all'):
            self.test_all_services()
        elif options.get('product_id'):
            self.test_product_notification(options['product_id'])
        else:
            self.test_all_services()
    
    def handle_config(self, options):
        """Mostrar configuración del sistema"""
        self.show_config()
    
    # === MÉTODOS DE FILTROS ===
    
    def list_filters(self):
        """Listar todas las reglas de filtros"""
        summary = filter_engine.get_rules_summary()
        
        self.stdout.write(self.style.SUCCESS(f'📋 FILTROS DE NOTIFICACIONES ({summary["total_rules"]} total, {summary["enabled_rules"]} activos)'))
        self.stdout.write('')
        
        for rule_info in summary['rules']:
            status = '✅' if rule_info['enabled'] else '❌'
            priority_icon = {'low': '🟢', 'normal': '🔵', 'high': '🟡', 'urgent': '🔴'}.get(rule_info['priority'], '🔵')
            
            self.stdout.write(f'{status} {priority_icon} {rule_info["name"]}')
            self.stdout.write(f'   📝 {rule_info["description"]}')
            self.stdout.write(f'   🔧 {rule_info["filters_count"]} filtros | 📡 {", ".join(rule_info["platforms"])}')
            self.stdout.write('')
    
    def add_filter(self, options):
        """Agregar nueva regla de filtro"""
        try:
            # Crear filtro
            filter_obj = NotificationFilter(
                field=options['field'],
                operator=FilterOperator(options['operator']),
                value=self._parse_value(options['value']),
                name=f"{options['field']}_{options['operator']}"
            )
            
            # Crear regla
            rule = NotificationRule(
                name=options['name'],
                filters=[filter_obj],
                priority=NotificationPriority(options['priority']),
                platforms=options['platforms'],
                template=options['template'],
                description=f"Regla personalizada para {options['field']}"
            )
            
            # Agregar a motor de filtros
            filter_engine.add_rule(rule)
            
            self.stdout.write(self.style.SUCCESS(f'✅ Regla "{options["name"]}" agregada exitosamente'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error agregando regla: {e}'))
    
    def remove_filter(self, name):
        """Eliminar regla de filtro"""
        try:
            filter_engine.remove_rule(name)
            self.stdout.write(self.style.SUCCESS(f'✅ Regla "{name}" eliminada'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error eliminando regla: {e}'))
    
    def toggle_filter(self, options):
        """Habilitar/deshabilitar regla de filtro"""
        name = options['name']
        if options.get('enable'):
            filter_engine.enable_rule(name, True)
            self.stdout.write(self.style.SUCCESS(f'✅ Regla "{name}" habilitada'))
        elif options.get('disable'):
            filter_engine.enable_rule(name, False)
            self.stdout.write(self.style.SUCCESS(f'⏸️ Regla "{name}" deshabilitada'))
        else:
            self.stdout.write(self.style.ERROR('❌ Debe especificar --enable o --disable'))
    
    # === MÉTODOS DE PLANTILLAS ===
    
    def list_templates(self):
        """Listar todas las plantillas"""
        summary = template_engine.get_templates_summary()
        
        self.stdout.write(self.style.SUCCESS(f'🎨 PLANTILLAS DE NOTIFICACIONES ({summary["total_templates"]} total, {summary["enabled_templates"]} activas)'))
        self.stdout.write('')
        
        for template_info in summary['templates']:
            status = '✅' if template_info['enabled'] else '❌'
            type_icon = {'text': '📝', 'markdown': '📋', 'html': '🌐', 'rich': '✨'}.get(template_info['type'], '📝')
            
            self.stdout.write(f'{status} {type_icon} {template_info["name"]}')
            self.stdout.write(f'   📝 {template_info["description"]}')
            self.stdout.write(f'   🔧 Variables: {", ".join(template_info["variables"][:5])}{"..." if len(template_info["variables"]) > 5 else ""}')
            self.stdout.write('')
    
    def preview_template(self, name):
        """Previsualizar plantilla"""
        preview = template_engine.preview_template(name)
        
        self.stdout.write(self.style.SUCCESS(f'👁️ PREVISUALIZACIÓN: {name}'))
        self.stdout.write('=' * 50)
        self.stdout.write(preview)
        self.stdout.write('=' * 50)
    
    def toggle_template(self, options):
        """Habilitar/deshabilitar plantilla"""
        name = options['name']
        if options.get('enable'):
            template_engine.enable_template(name, True)
            self.stdout.write(self.style.SUCCESS(f'✅ Plantilla "{name}" habilitada'))
        elif options.get('disable'):
            template_engine.enable_template(name, False)
            self.stdout.write(self.style.SUCCESS(f'⏸️ Plantilla "{name}" deshabilitada'))
        else:
            self.stdout.write(self.style.ERROR('❌ Debe especificar --enable o --disable'))
    
    # === MÉTODOS DE ESTADÍSTICAS ===
    
    def show_stats(self):
        """Mostrar estadísticas del sistema"""
        stats = notification_manager.get_system_stats()
        
        self.stdout.write(self.style.SUCCESS('📊 ESTADÍSTICAS DEL SISTEMA DE NOTIFICACIONES'))
        self.stdout.write('')
        
        # Servicios
        self.stdout.write(f'📡 Servicios activos: {stats["total_active_services"]}/2')
        for service_name, service_stats in stats['services'].items():
            status = '✅' if service_stats['enabled'] else '❌'
            self.stdout.write(f'   {status} {service_name.title()}: {service_stats["sent"]} enviadas | {service_stats["failed"]} fallidas | {service_stats["filtered"]} filtradas')
            self.stdout.write(f'       Última: {service_stats["last_sent_formatted"]}')
        
        self.stdout.write('')
        
        # Filtros
        filters_stats = stats['filters']
        self.stdout.write(f'🔧 Filtros: {filters_stats["enabled_rules"]}/{filters_stats["total_rules"]} activos')
        
        # Plantillas
        templates_stats = stats['templates']
        self.stdout.write(f'🎨 Plantillas: {templates_stats["enabled_templates"]}/{templates_stats["total_templates"]} activas')
    
    # === MÉTODOS DE PRUEBA ===
    
    def test_all_services(self):
        """Probar todos los servicios"""
        self.stdout.write(self.style.SUCCESS('🧪 PROBANDO SERVICIOS DE NOTIFICACIÓN...'))
        
        results = notification_manager.test_notifications()
        
        for service_name, success in results.items():
            status = '✅' if success else '❌'
            self.stdout.write(f'{status} {service_name.title()}: {"Exitoso" if success else "Falló"}')
    
    def test_product_notification(self, product_id):
        """Probar notificación con producto específico"""
        try:
            product = Product.objects.get(id=product_id)
            
            self.stdout.write(self.style.SUCCESS(f'🧪 PROBANDO NOTIFICACIÓN CON PRODUCTO: {product.title}'))
            
            results = notification_manager.notify_new_product(product)
            
            for service_name, result in results.items():
                if result['sent']:
                    self.stdout.write(self.style.SUCCESS(f'✅ {service_name}: Enviado (plantilla: {result["template_used"]})'))
                elif result['filtered']:
                    self.stdout.write(self.style.WARNING(f'🔒 {service_name}: Filtrado - {result["error"]}'))
                else:
                    self.stdout.write(self.style.ERROR(f'❌ {service_name}: Error - {result["error"]}'))
                
                if result.get('rules_matched'):
                    self.stdout.write(f'   📋 Reglas coincidentes: {", ".join(result["rules_matched"])}')
            
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Producto con ID {product_id} no encontrado'))
    
    # === MÉTODOS DE CONFIGURACIÓN ===
    
    def show_config(self):
        """Mostrar configuración del sistema"""
        self.stdout.write(self.style.SUCCESS('⚙️ CONFIGURACIÓN DEL SISTEMA'))
        self.stdout.write('')
        
        # Configuración de servicios
        for service_name, service in notification_manager.services.items():
            status = '✅ Configurado' if service.enabled else '❌ No configurado'
            self.stdout.write(f'📡 {service_name.title()}: {status}')
        
        self.stdout.write('')
        self.stdout.write('🔧 Variables de entorno requeridas:')
        self.stdout.write('   - TELEGRAM_BOT_TOKEN')
        self.stdout.write('   - TELEGRAM_CHAT_ID')
        self.stdout.write('   - DISCORD_WEBHOOK_URL')
    
    # === MÉTODOS AUXILIARES ===
    
    def _parse_value(self, value_str):
        """Parsear valor según tipo"""
        # Intentar convertir a número
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Verificar si es lista
        if value_str.startswith('[') and value_str.endswith(']'):
            try:
                return json.loads(value_str)
            except json.JSONDecodeError:
                pass
        
        # Verificar boolean
        if value_str.lower() in ['true', 'false']:
            return value_str.lower() == 'true'
        
        # Devolver como string
        return value_str
    
    def print_help(self):
        """Mostrar ayuda del comando"""
        self.stdout.write(self.style.SUCCESS('🔔 GESTIÓN DEL SISTEMA DE NOTIFICACIONES'))
        self.stdout.write('')
        self.stdout.write('Comandos disponibles:')
        self.stdout.write('  filters list                    - Listar reglas de filtros')
        self.stdout.write('  filters add --name NOMBRE ...   - Agregar regla de filtro')
        self.stdout.write('  filters remove NOMBRE           - Eliminar regla de filtro')
        self.stdout.write('  filters toggle NOMBRE --enable  - Habilitar/deshabilitar regla')
        self.stdout.write('')
        self.stdout.write('  templates list                  - Listar plantillas')
        self.stdout.write('  templates preview NOMBRE        - Previsualizar plantilla')
        self.stdout.write('  templates toggle NOMBRE --enable - Habilitar/deshabilitar plantilla')
        self.stdout.write('')
        self.stdout.write('  stats                           - Ver estadísticas')
        self.stdout.write('  stats --reset                   - Reiniciar estadísticas')
        self.stdout.write('')
        self.stdout.write('  test --all                      - Probar todos los servicios')
        self.stdout.write('  test --product-id ID            - Probar con producto específico')
        self.stdout.write('')
        self.stdout.write('  config                          - Mostrar configuración')