"""
Señales de Django para la aplicación de productos
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product
from .services.notifications import notify_new_product

logger = logging.getLogger('products')


@receiver(post_save, sender=Product)
def product_created_notification(sender, instance, created, **kwargs):
    """
    Enviar notificación cuando se crea un nuevo producto
    """
    if created:  # Solo para productos nuevos
        try:
            logger.info(f"Enviando notificación para nuevo producto: {instance.title}")
            results = notify_new_product(instance)
            
            # Log de resultados
            for service, success in results.items():
                if success:
                    logger.info(f"Notificación enviada exitosamente por {service}")
                else:
                    logger.warning(f"Error enviando notificación por {service}")
                    
        except Exception as e:
            logger.error(f"Error en señal de notificación para producto {instance.id}: {e}")