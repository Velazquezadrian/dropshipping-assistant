"""
Sistema de notificaciones para productos de dropshipping
Soporta notificaciones por Telegram y Discord
"""

import logging
import asyncio
import requests
from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
from products.models import Product

logger = logging.getLogger('products')


class BaseNotificationService:
    """Clase base para servicios de notificación"""
    
    def __init__(self):
        self.enabled = self.is_configured()
    
    def is_configured(self) -> bool:
        """Verificar si el servicio está configurado correctamente"""
        raise NotImplementedError
    
    def send_notification(self, message: str, **kwargs) -> bool:
        """Enviar notificación"""
        raise NotImplementedError
    
    def format_product_message(self, product: Product) -> str:
        """Formatear mensaje para un producto"""
        message = f"""
🛍️ **Nuevo Producto Encontrado**

📝 **Título:** {product.title}
💰 **Precio:** ${product.price}
⭐ **Calificación:** {product.rating or 'N/A'}/5
🚚 **Envío:** {product.shipping_time or 'N/A'} días
🏷️ **Categoría:** {product.category or 'N/A'}
🌐 **Plataforma:** {product.source_platform}
🔗 **URL:** {product.url}

⏰ Agregado el {product.created_at.strftime('%d/%m/%Y %H:%M')}
        """.strip()
        return message
    
    def format_bulk_message(self, products: List[Product]) -> str:
        """Formatear mensaje para múltiples productos"""
        if not products:
            return "No hay productos nuevos."
        
        count = len(products)
        avg_price = sum(p.price for p in products) / count
        platforms = list(set(p.source_platform for p in products))
        
        message = f"""
🛍️ **{count} Nuevos Productos Encontrados**

📊 **Resumen:**
💰 Precio promedio: ${avg_price:.2f}
🌐 Plataformas: {', '.join(platforms)}

📝 **Productos:**
        """.strip()
        
        for i, product in enumerate(products[:5], 1):  # Máximo 5 productos
            message += f"\n{i}. {product.title} - ${product.price}"
        
        if count > 5:
            message += f"\n... y {count - 5} productos más"
        
        return message


class TelegramNotificationService(BaseNotificationService):
    """Servicio de notificaciones para Telegram"""
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
        super().__init__()
    
    def is_configured(self) -> bool:
        """Verificar configuración de Telegram"""
        return bool(self.bot_token and self.chat_id)
    
    def send_notification(self, message: str, parse_mode: str = 'Markdown') -> bool:
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
            'disable_web_page_preview': True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Notificación enviada por Telegram exitosamente")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error enviando notificación por Telegram: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en Telegram: {e}")
            return False


class DiscordNotificationService(BaseNotificationService):
    """Servicio de notificaciones para Discord"""
    
    def __init__(self):
        self.webhook_url = getattr(settings, 'DISCORD_WEBHOOK_URL', '')
        super().__init__()
    
    def is_configured(self) -> bool:
        """Verificar configuración de Discord"""
        return bool(self.webhook_url)
    
    def send_notification(self, message: str, username: str = "Dropship Bot") -> bool:
        """
        Enviar notificación por Discord
        
        Args:
            message: Mensaje a enviar
            username: Nombre del bot
            
        Returns:
            bool: True si se envió correctamente
        """
        if not self.enabled:
            logger.warning("Discord no está configurado correctamente")
            return False
        
        payload = {
            'content': message,
            'username': username
        }
        
        try:
            response = requests.post(self.webhook_url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info("Notificación enviada por Discord exitosamente")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error enviando notificación por Discord: {e}")
            return False
        except Exception as e:
            logger.error(f"Error inesperado en Discord: {e}")
            return False
    
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
    """Gestor principal de notificaciones"""
    
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
    
    def notify_new_product(self, product: Product) -> Dict[str, bool]:
        """
        Notificar sobre un nuevo producto
        
        Args:
            product: Producto a notificar
            
        Returns:
            Dict: Resultado de envío por cada servicio
        """
        if not self.active_services:
            logger.warning("No hay servicios de notificación configurados")
            return {}
        
        results = {}
        
        for service_name, service in self.active_services.items():
            try:
                message = service.format_product_message(product)
                success = service.send_notification(message)
                results[service_name] = success
                
                if success:
                    logger.info(f"Notificación de producto enviada por {service_name}")
                else:
                    logger.error(f"Error enviando notificación por {service_name}")
                    
            except Exception as e:
                logger.error(f"Error inesperado notificando por {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    def notify_bulk_products(self, products: List[Product]) -> Dict[str, bool]:
        """
        Notificar sobre múltiples productos
        
        Args:
            products: Lista de productos a notificar
            
        Returns:
            Dict: Resultado de envío por cada servicio
        """
        if not products:
            return {}
        
        if not self.active_services:
            logger.warning("No hay servicios de notificación configurados")
            return {}
        
        results = {}
        
        for service_name, service in self.active_services.items():
            try:
                message = service.format_bulk_message(products)
                success = service.send_notification(message)
                results[service_name] = success
                
                if success:
                    logger.info(f"Notificación masiva enviada por {service_name} ({len(products)} productos)")
                else:
                    logger.error(f"Error enviando notificación masiva por {service_name}")
                    
            except Exception as e:
                logger.error(f"Error inesperado en notificación masiva por {service_name}: {e}")
                results[service_name] = False
        
        return results
    
    def notify_scraping_summary(self, total_new: int, total_existing: int, total_errors: int = 0) -> Dict[str, bool]:
        """
        Notificar resumen de scraping
        
        Args:
            total_new: Productos nuevos encontrados
            total_existing: Productos que ya existían
            total_errors: Errores durante el scraping
            
        Returns:
            Dict: Resultado de envío por cada servicio
        """
        if not self.active_services:
            return {}
        
        message = f"""
📊 **Resumen de Scraping**

✅ Productos nuevos: {total_new}
♻️ Productos existentes: {total_existing}
❌ Errores: {total_errors}

⏰ {timezone.now().strftime('%d/%m/%Y %H:%M')}
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
🧪 **Test de Notificaciones**

Este es un mensaje de prueba del sistema de notificaciones del Dropship Bot.

⏰ {timezone.now().strftime('%d/%m/%Y %H:%M')}
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


# Instancia global del gestor
notification_manager = NotificationManager()


def notify_new_product(product: Product) -> Dict[str, bool]:
    """Función conveniente para notificar un nuevo producto"""
    return notification_manager.notify_new_product(product)


def notify_bulk_products(products: List[Product]) -> Dict[str, bool]:
    """Función conveniente para notificar múltiples productos"""
    return notification_manager.notify_bulk_products(products)


def notify_scraping_summary(total_new: int, total_existing: int, total_errors: int = 0) -> Dict[str, bool]:
    """Función conveniente para notificar resumen de scraping"""
    return notification_manager.notify_scraping_summary(total_new, total_existing, total_errors)