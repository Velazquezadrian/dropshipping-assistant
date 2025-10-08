"""
🔔 Sistema Avanzado de Notificaciones para Dropshipping Assistant
Filtros inteligentes, plantillas personalizadas y alertas condicionales
"""

import logging
import requests
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from products.models import Product
from products.services.notification_filters import filter_engine, NotificationRule, NotificationPriority
from products.services.notification_templates import template_engine

logger = logging.getLogger('notifications')


class BaseNotificationService:
    """Clase base para servicios de notificación con sistema avanzado"""
    
    def __init__(self):
        self.enabled = True
        self.rate_limit = 60  # segundos entre mensajes
        self.last_notification = None
        self.platform_name = "base"
        self.notification_stats = {
            'sent': 0,
            'failed': 0,
            'filtered': 0,
            'last_sent': None
        }
    
    def send_notification(self, message: str, **kwargs) -> bool:
        """Enviar notificación - implementar en subclases"""
        raise NotImplementedError
    
    def send_product_notification(self, product: Product) -> Dict[str, Any]:
        """
        Enviar notificación de producto con filtros y plantillas
        
        Args:
            product: Producto para notificar
            
        Returns:
            Dict con resultado del envío
        """
        result = {
            'sent': False,
            'filtered': False,
            'rules_matched': [],
            'template_used': None,
            'error': None,
            'platform': self.platform_name
        }
        
        try:
            # Evaluar producto contra reglas de filtros
            matching_rules = filter_engine.evaluate_product(product)
            
            if not matching_rules:
                result['filtered'] = True
                result['error'] = "Producto no cumple ninguna regla de filtro"
                self.notification_stats['filtered'] += 1
                logger.debug(f"Producto {product.title} filtrado - no cumple reglas")
                return result
            
            # Usar la regla de mayor prioridad
            top_rule = self._get_highest_priority_rule(matching_rules)
            result['rules_matched'] = [rule.name for rule in matching_rules]
            
            # Verificar si esta plataforma está habilitada para la regla
            if self.platform_name not in top_rule.platforms:
                result['filtered'] = True
                result['error'] = f"Plataforma {self.platform_name} no habilitada para regla {top_rule.name}"
                return result
            
            # Renderizar notificación usando plantilla
            notification_data = template_engine.render_notification(
                template_name=top_rule.template,
                product=product,
                priority=top_rule.priority,
                platform=self.platform_name
            )
            
            result['template_used'] = top_rule.template
            
            # Enviar notificación
            success = self._send_rendered_notification(notification_data, product)
            
            if success:
                result['sent'] = True
                self.notification_stats['sent'] += 1
                self.notification_stats['last_sent'] = datetime.now()
                logger.info(f"Notificación enviada a {self.platform_name} para producto {product.title}")
            else:
                result['error'] = "Fallo en envío de notificación"
                self.notification_stats['failed'] += 1
            
        except Exception as e:
            result['error'] = str(e)
            self.notification_stats['failed'] += 1
            logger.error(f"Error enviando notificación a {self.platform_name}: {e}")
        
        return result
    
    def _get_highest_priority_rule(self, rules: List[NotificationRule]) -> NotificationRule:
        """Obtener regla de mayor prioridad"""
        priority_order = {
            NotificationPriority.URGENT: 4,
            NotificationPriority.HIGH: 3,
            NotificationPriority.NORMAL: 2,
            NotificationPriority.LOW: 1
        }
        
        return max(rules, key=lambda r: priority_order.get(r.priority, 0))
    
    def _send_rendered_notification(self, notification_data: Dict[str, Any], product: Product) -> bool:
        """Enviar notificación renderizada - implementar en subclases"""
        raise NotImplementedError
    
    
    def send_bulk_notification(self, products: List[Product], title: str = "Productos Encontrados") -> Dict[str, Any]:
        """Enviar notificación con múltiples productos"""
        result = {
            'sent': False,
            'products_processed': len(products),
            'notifications_sent': 0,
            'error': None
        }
        
        try:
            if not products:
                result['error'] = "No hay productos para notificar"
                return result
            
            # Enviar notificación individual para cada producto que cumpla filtros
            notifications_sent = 0
            for product in products:
                product_result = self.send_product_notification(product)
                if product_result['sent']:
                    notifications_sent += 1
            
            result['notifications_sent'] = notifications_sent
            result['sent'] = notifications_sent > 0
            
            # Si no se envió ninguna notificación individual, enviar resumen
            if notifications_sent == 0:
                summary_message = self._create_summary_message(products, title)
                if summary_message:
                    success = self.send_notification(summary_message)
                    if success:
                        result['sent'] = True
                        result['notifications_sent'] = 1
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error enviando notificación bulk a {self.platform_name}: {e}")
        
        return result
    
    def _create_summary_message(self, products: List[Product], title: str) -> str:
        """Crear mensaje resumen cuando no hay productos que cumplan filtros"""
        if not products:
            return ""
        
        # Usar plantilla compacta para resumen
        summary_data = template_engine.render_notification(
            template_name="compact",
            product=products[0],  # Usar primer producto como ejemplo
            priority=NotificationPriority.LOW,
            platform=self.platform_name
        )
        
        message = f"� **{title}** ({len(products)} productos encontrados)\n\n"
        message += "Los productos no cumplen los filtros activos para notificaciones individuales.\n\n"
        
        # Mostrar estadísticas
        categories = {}
        total_products = len(products)
        avg_price = sum(float(p.price or 0) for p in products) / total_products if total_products > 0 else 0
        
        for product in products:
            cat = product.category or "Sin categoría"
            categories[cat] = categories.get(cat, 0) + 1
        
        message += f"📊 **Estadísticas:**\n"
        message += f"• Total productos: {total_products}\n"
        message += f"• Precio promedio: ${avg_price:.2f}\n"
        message += f"• Categorías principales: {', '.join(list(categories.keys())[:3])}\n"
        
        return message
    
    def format_product_message(self, product: Product) -> str:
        """Formatear mensaje de producto (método legacy)"""
        # Usar plantilla por defecto
        notification_data = template_engine.render_notification(
            template_name="default",
            product=product,
            priority=NotificationPriority.NORMAL,
            platform=self.platform_name
        )
        return notification_data['body']


class TelegramNotificationService(BaseNotificationService):
    """Servicio de notificaciones para Telegram con sistema avanzado"""
    
    def __init__(self):
        super().__init__()
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
        self.platform_name = "telegram"
        self.enabled = self.is_configured()
    
    def is_configured(self) -> bool:
        """Verificar configuración de Telegram"""
        return bool(self.bot_token and self.chat_id)
    
    def send_notification(self, message: str, parse_mode: str = 'Markdown', **kwargs) -> bool:
        """
        Enviar notificación por Telegram
        
        Args:
            message: Mensaje a enviar
            parse_mode: Modo de parseo (Markdown o HTML)
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.enabled:
            logger.warning("Telegram no está configurado correctamente")
            return False
        
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        
        payload = {
            'chat_id': self.chat_id,
            'text': message,
            'parse_mode': parse_mode,
            'disable_web_page_preview': kwargs.get('disable_preview', True)
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Notificación enviada por Telegram exitosamente")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error enviando notificación por Telegram: {e}")
            return False
    
    def _send_rendered_notification(self, notification_data: Dict[str, Any], product: Product) -> bool:
        """Enviar notificación renderizada por Telegram"""
        try:
            # Obtener configuración de plataforma
            platform_config = notification_data.get('platform_config', {})
            parse_mode = platform_config.get('parse_mode', 'Markdown')
            disable_preview = platform_config.get('disable_preview', True)
            
            # Enviar notificación
            message = notification_data['body']
            return self.send_notification(
                message=message,
                parse_mode=parse_mode,
                disable_preview=disable_preview
            )
            
        except Exception as e:
            logger.error(f"Error enviando notificación renderizada por Telegram: {e}")
            return False
    
    def format_bulk_message(self, products: List[Product], title: str = "Productos Encontrados") -> str:
        """Formatear mensaje con múltiples productos (método legacy)"""
        return self._create_summary_message(products, title)
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de notificaciones"""
        stats = self.notification_stats.copy()
        stats['platform'] = self.platform_name
        stats['enabled'] = self.enabled
        stats['last_sent_formatted'] = (
            stats['last_sent'].strftime("%d/%m/%Y %H:%M:%S") 
            if stats['last_sent'] else "Nunca"
        )
        return stats
    
    def reset_stats(self):
        """Reiniciar estadísticas"""
        self.notification_stats = {
            'sent': 0,
            'failed': 0,
            'filtered': 0,
            'last_sent': None
        }


class DiscordNotificationService(BaseNotificationService):
    """Servicio de notificaciones para Discord con sistema avanzado"""
    
    def __init__(self):
        super().__init__()
        self.webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', '')
        self.platform_name = "discord"
        self.enabled = self.is_configured()
    
    def is_configured(self) -> bool:
        """Verificar configuración de Discord"""
        return bool(self.webhook_url and self.webhook_url.strip())
    
    def send_notification(self, message: str = None, embed: Dict[str, Any] = None, username: str = "Dropship Bot", **kwargs) -> bool:
        """
        Enviar notificación por Discord
        
        Args:
            message: Mensaje a enviar (texto simple)
            embed: Embed de Discord (formato rico)
            username: Nombre del bot
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.enabled:
            logger.debug("Discord webhook no configurado - saltando notificación")
            return True  # Retornar True para no marcar como error
        
        if not self.webhook_url.strip():
            logger.debug("Discord webhook vacío - saltando notificación")
            return True  # Retornar True para no marcar como error
        
        payload = {
            'username': username
        }
        
        if message:
            payload['content'] = message
        
        if embed:
            payload['embeds'] = [embed] if not isinstance(embed, list) else embed
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Notificación enviada por Discord exitosamente")
            return True
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.warning("Discord webhook no autorizado (401) - verifica la URL del webhook")
                # Desactivar temporalmente para evitar spam de errores
                self.enabled = False
            else:
                logger.error(f"Error HTTP enviando notificación por Discord: {e}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error enviando notificación por Discord: {e}")
            return False
    
    def _send_rendered_notification(self, notification_data: Dict[str, Any], product: Product) -> bool:
        """Enviar notificación renderizada por Discord"""
        try:
            platform_config = notification_data.get('platform_config', {})
            
            # Si la configuración incluye embeds, usar formato rico
            if platform_config.get('embed', False) and 'embeds' in notification_data:
                return self.send_notification(
                    embed=notification_data['embeds'][0],
                    username="Dropship Assistant 🛍️"
                )
            else:
                # Usar mensaje de texto simple
                return self.send_notification(
                    message=notification_data['body'],
                    username="Dropship Assistant 🛍️"
                )
                
        except Exception as e:
            logger.error(f"Error enviando notificación renderizada por Discord: {e}")
            return False
    
    def format_bulk_message(self, products: List[Product], title: str = "Productos Encontrados") -> str:
        """Formatear mensaje con múltiples productos (método legacy)"""
        return self._create_summary_message(products, title)
    
    def get_notification_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de notificaciones"""
        stats = self.notification_stats.copy()
        stats['platform'] = self.platform_name
        stats['enabled'] = self.enabled
        stats['last_sent_formatted'] = (
            stats['last_sent'].strftime("%d/%m/%Y %H:%M:%S") 
            if stats['last_sent'] else "Nunca"
        )
        return stats
    
    def reset_stats(self):
        """Reiniciar estadísticas"""
        self.notification_stats = {
            'sent': 0,
            'failed': 0,
            'filtered': 0,
            'last_sent': None
        }
    
    def format_product_message(self, product: Product) -> str:
        """Formatear mensaje para Discord (sin Markdown)"""
        message = f"""
🛍️ **Nuevo Producto Encontrado**

📝 Título: {product.title}
💰 Precio: ${product.price}
⭐ Calificación: {product.rating or 'N/A'}/5
🚚 Envío: {product.shipping_time or 'N/A'} días
🏷️ Categoría: {product.category or 'N/A'}
🌐 Plataforma: {product.source_platform}
🔗 URL: {product.url}

⏰ Agregado el {product.created_at.strftime('%d/%m/%Y %H:%M')}
        """.strip()
        return message


class NotificationManager:
    """Gestor principal de notificaciones con sistema avanzado"""
    
    def __init__(self):
        self.services = {
            'telegram': TelegramNotificationService(),
            'discord': DiscordNotificationService()
        }
        
        # Servicios activos (configurados)
        self.active_services = {
            name: service for name, service in self.services.items()
            if service.enabled
        }
        
        logger.info(f"Servicios de notificación activos: {list(self.active_services.keys())}")
    
    def notify_new_product(self, product: Product) -> Dict[str, Dict[str, Any]]:
        """
        Notificar sobre un nuevo producto usando sistema avanzado
        
        Args:
            product: Producto a notificar
            
        Returns:
            Dict: Resultado detallado de envío por cada servicio
        """
        if not self.active_services:
            logger.warning("No hay servicios de notificación configurados")
            return {}
        
        results = {}
        
        for service_name, service in self.active_services.items():
            try:
                result = service.send_product_notification(product)
                results[service_name] = result
                
                if result['sent']:
                    logger.info(f"Producto notificado exitosamente a {service_name}")
                elif result['filtered']:
                    logger.debug(f"Producto filtrado para {service_name}: {result['error']}")
                else:
                    logger.warning(f"Fallo notificando producto a {service_name}: {result['error']}")
                    
            except Exception as e:
                logger.error(f"Error notificando producto a {service_name}: {e}")
                results[service_name] = {
                    'sent': False,
                    'filtered': False,
                    'error': str(e),
                    'platform': service_name
                }
        
        return results
    
    def notify_bulk_products(self, products: List[Product], title: str = "Productos Encontrados") -> Dict[str, Dict[str, Any]]:
        """
        Notificar múltiples productos
        
        Args:
            products: Lista de productos
            title: Título para la notificación
            
        Returns:
            Dict: Resultado de envío por cada servicio
        """
        if not self.active_services:
            logger.warning("No hay servicios de notificación configurados")
            return {}
        
        results = {}
        
        for service_name, service in self.active_services.items():
            try:
                result = service.send_bulk_notification(products, title)
                results[service_name] = result
            except Exception as e:
                logger.error(f"Error enviando bulk a {service_name}: {e}")
                results[service_name] = {
                    'sent': False,
                    'error': str(e),
                    'products_processed': len(products),
                    'notifications_sent': 0
                }
        
        return results
    
    def notify_scraping_summary(self, total_new: int, total_existing: int, total_errors: int = 0) -> Dict[str, bool]:
        """
        Notificar resumen de scraping
        
        Args:
            total_new: Productos nuevos encontrados
            total_existing: Productos ya existentes
            total_errors: Errores en el scraping
            
        Returns:
            Dict: Resultado de envío por cada servicio
        """
        message = f"""
📊 **Resumen de Scraping**

✅ **Nuevos productos:** {total_new}
🔄 **Ya existentes:** {total_existing}
❌ **Errores:** {total_errors}

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
        
        results = {}
        
        for service_name, service in self.active_services.items():
            try:
                success = service.send_notification(message)
                results[service_name] = success
            except Exception as e:
                logger.error(f"Error enviando resumen por {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    def test_notifications(self) -> Dict[str, bool]:
        """
        Probar todos los servicios de notificación
        
        Returns:
            Dict: Resultado de prueba por cada servicio
        """
        test_message = f"""
🧪 **Test de Notificaciones Avanzadas**

Sistema de notificaciones con filtros y plantillas funcionando correctamente.

🔧 **Características activas:**
• Filtros inteligentes de productos
• Plantillas personalizadas
• Rate limiting y programación
• Múltiples plataformas

⏰ {datetime.now().strftime('%d/%m/%Y %H:%M')}
        """.strip()
        
        results = {}
        
        for service_name, service in self.services.items():
            try:
                if service.enabled:
                    success = service.send_notification(test_message)
                    results[service_name] = success
                else:
                    results[service_name] = False
                    logger.warning(f"Servicio {service_name} no está configurado")
            except Exception as e:
                logger.error(f"Error probando {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de notificaciones"""
        stats = {
            'services': {},
            'filters': filter_engine.get_rules_summary(),
            'templates': template_engine.get_templates_summary(),
            'total_active_services': len(self.active_services)
        }
        
        for service_name, service in self.services.items():
            stats['services'][service_name] = service.get_notification_stats()
        
        return stats
    
    def reset_all_stats(self):
        """Reiniciar estadísticas de todos los servicios"""
        for service in self.services.values():
            service.reset_stats()
        logger.info("Estadísticas de notificaciones reiniciadas")


# Instancia global del gestor
notification_manager = NotificationManager()


def notify_new_product(product: Product) -> Dict[str, Dict[str, Any]]:
    """Función conveniente para notificar un nuevo producto"""
    return notification_manager.notify_new_product(product)


def notify_bulk_products(products: List[Product], title: str = "Productos Encontrados") -> Dict[str, Dict[str, Any]]:
    """Función conveniente para notificar múltiples productos"""
    return notification_manager.notify_bulk_products(products, title)


def notify_scraping_summary(total_new: int, total_existing: int, total_errors: int = 0) -> Dict[str, bool]:
    """Función conveniente para notificar resumen de scraping"""
    return notification_manager.notify_scraping_summary(total_new, total_existing, total_errors)


def notify_scraping_summary_with_product(total_new: int, total_existing: int, total_errors: int = 0, latest_product=None) -> Dict[str, bool]:
    """Función para notificar resumen de scraping con producto destacado para dropshipping"""
    import requests
    
    results = {}
    
    if total_new == 0:
        return {'discord': True, 'telegram': True}  # No enviar si no hay productos nuevos
    
    # Notificación Discord con producto destacado
    try:
        webhook_url = "https://discord.com/api/webhooks/1423036583338053793/Vsy9uz72Gpk9zv5-M8wtLeM-ISj-CPJ-LK73TcKVFL7R2s6I8F8kG77d32zT0ekcWgDL"
        
        message = f"🔥 **¡OFERTA ESPECIAL DETECTADA!**\n\n🔥 **¡OFERTA ESPECIAL!** 🔥"
        
        if latest_product:
            embed = {
                'title': '🛍️ Nuevo Producto para Dropshipping',
                'description': f'**{latest_product.title}**\n\n[🛒 **VER PRODUCTO EN ALIEXPRESS**]({latest_product.url})',
                'color': 0xff6b00,  # Naranja como AliExpress
                'fields': [
                    {'name': '💰 Precio', 'value': f'${latest_product.price}', 'inline': True},
                    {'name': '⭐ Rating', 'value': f'{latest_product.rating}/5.0', 'inline': True},
                    {'name': '🚚 Envío', 'value': f'{latest_product.shipping_time} días', 'inline': True},
                    {'name': '⚡ Categoría', 'value': str(latest_product.category), 'inline': True},
                    {'name': '🎯 Fuente', 'value': 'AliExpress', 'inline': True},
                    {'name': '📦 Productos nuevos', 'value': str(total_new), 'inline': True}
                ],
                'footer': {'text': 'Dropshipping Assistant | aliexpress_advanced'},
                'timestamp': '2025-10-08T17:00:00Z'
            }
        else:
            embed = {
                'title': '🛍️ Scraping Automático Completado',
                'description': f'Se encontraron {total_new} productos nuevos',
                'color': 0x00ff00,
                'fields': [
                    {'name': '🆕 Nuevos', 'value': str(total_new), 'inline': True},
                    {'name': '📋 Existentes', 'value': str(total_existing), 'inline': True},
                    {'name': '❌ Errores', 'value': str(total_errors), 'inline': True}
                ],
                'footer': {'text': 'Dropship Assistant - Sistema Automático'},
                'timestamp': '2025-10-08T17:00:00Z'
            }
        
        payload = {
            'username': 'Dropship Assistant 🛍️',
            'content': message,
            'embeds': [embed]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        results['discord'] = response.status_code in [200, 204]
        
    except Exception as e:
        logger.error(f"Error en notificación Discord: {e}")
        results['discord'] = False
    
    # Notificación Telegram
    try:
        bot_token = "8426879269:AAFiOdQvZEuBWjh3CQOalbCI1JZaIobRhtM"
        chat_id = "1301431585"
        
        if latest_product:
            message = f"""🔥 *¡OFERTA ESPECIAL DETECTADA!*

🛍️ *{latest_product.title}*

💰 *PRECIO INCREÍBLE:* ${latest_product.price}
⭐ *Rating:* {latest_product.rating}/5.0
⚡ *Categoría:* {latest_product.category}
🚚 *Envío:* {latest_product.shipping_time} días
🎯 *Fuente:* AliExpress

🛒 *ENLACE DEL PRODUCTO:*
{latest_product.url}

🚨 *¡PRECIO MUY BAJO!* 🚨
Esta oferta podría terminar pronto

_Dropship Assistant - Sistema Automático_"""
        else:
            message = f"""🤖 *Sistema Automático - Scraping Completado*

✅ *{total_new} productos nuevos encontrados*
📋 *{total_existing} productos ya existían*
❌ *{total_errors} errores*

_Dropship Assistant - Funcionando automáticamente_"""
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'Markdown',
            'disable_web_page_preview': False
        }
        
        response = requests.post(url, json=payload, timeout=10)
        results['telegram'] = response.status_code == 200
        
    except Exception as e:
        logger.error(f"Error en notificación Telegram: {e}")
        results['telegram'] = False
    
    return results


def test_all_notifications() -> Dict[str, bool]:
    """Función conveniente para probar todas las notificaciones"""
    return notification_manager.test_notifications()


def get_notification_system_stats() -> Dict[str, Any]:
    """Función conveniente para obtener estadísticas del sistema"""
    return notification_manager.get_system_stats()


def reset_notification_stats():
    """Función conveniente para reiniciar estadísticas"""
    notification_manager.reset_all_stats()