"""
Tareas programadas (cron jobs) para el dropship bot
"""

import logging
from django.utils import timezone
from products.models import Product
from products.services.scraper import scrape_all_platforms
from products.services.notifications import notify_scraping_summary

logger = logging.getLogger('products')


def scrape_products():
    """
    Tarea cron para scrapear productos periódicamente
    Esta función será ejecutada por django-crontab
    """
    logger.info("Iniciando tarea programada de scraping")
    
    try:
        # Configuración de scraping
        products_per_platform = 5
        
        # Ejecutar scraping
        products = scrape_all_platforms(count_per_platform=products_per_platform)
        logger.info(f"Scraping completado: {len(products)} productos obtenidos")
        
        # Procesar productos
        from products.services.product_manager import bulk_import_products
        
        stats = bulk_import_products(products)
        new_products = stats['created']
        existing_products = stats['existing']
        errors = stats['errors']
        
        # Enviar resumen por notificaciones
        if new_products > 0 or errors > 0:  # Solo notificar si hay algo relevante
            notify_scraping_summary(new_products, existing_products, errors)
        
        # Log final
        logger.info(
            f"Tarea cron completada: {new_products} nuevos, "
            f"{existing_products} existentes, {errors} errores"
        )
        
        return f"Cron ejecutado: {new_products} nuevos productos agregados"
        
    except Exception as e:
        logger.error(f"Error crítico en tarea cron de scraping: {e}")
        
        # Notificar error crítico
        try:
            notify_scraping_summary(0, 0, 1)
        except:
            pass  # Evitar loop infinito de errores
        
        raise e


def cleanup_old_products():
    """
    Tarea cron para limpiar productos antiguos (opcional)
    Mantiene solo los productos de los últimos 30 días
    """
    logger.info("Iniciando limpieza de productos antiguos")
    
    try:
        from datetime import timedelta
        
        # Productos más antiguos que 30 días
        cutoff_date = timezone.now() - timedelta(days=30)
        old_products = Product.objects.filter(created_at__lt=cutoff_date)
        
        count = old_products.count()
        if count > 0:
            old_products.delete()
            logger.info(f"Eliminados {count} productos antiguos")
        else:
            logger.info("No hay productos antiguos para eliminar")
        
        return f"Limpieza completada: {count} productos eliminados"
        
    except Exception as e:
        logger.error(f"Error en limpieza de productos: {e}")
        raise e


def health_check_cron():
    """
    Tarea cron para verificar salud del sistema
    """
    logger.info("Ejecutando health check programado")
    
    try:
        # Verificar base de datos
        total_products = Product.objects.count()
        recent_products = Product.objects.filter(
            created_at__gte=timezone.now() - timezone.timedelta(hours=24)
        ).count()
        
        # Log de estadísticas
        logger.info(f"Health check: {total_products} productos totales, {recent_products} en 24h")
        
        # Verificar si hay productos recientes (scraping funcionando)
        if recent_products == 0:
            logger.warning("No se han agregado productos en las últimas 24 horas")
        
        return f"Health check OK: {total_products} productos totales"
        
    except Exception as e:
        logger.error(f"Error en health check: {e}")
        raise e