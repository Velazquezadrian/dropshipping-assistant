"""
Servicio de gestión de productos con lógica de idempotencia
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from decimal import Decimal
from django.db import IntegrityError, transaction
from django.utils import timezone
from products.models import Product

logger = logging.getLogger('products')


class ProductManager:
    """Gestor de productos con lógica de idempotencia y validación"""
    
    @staticmethod
    def create_or_update_product(product_data: Dict[str, Any], update_existing: bool = False) -> Tuple[Product, bool]:
        """
        Crea o actualiza un producto con lógica de idempotencia
        
        Args:
            product_data: Datos del producto
            update_existing: Si True, actualiza productos existentes
            
        Returns:
            Tuple[Product, bool]: (producto, fue_creado)
        """
        url = product_data.get('url')
        if not url:
            raise ValueError("URL es requerida para idempotencia")
        
        try:
            # Buscar producto existente por URL
            existing_product = Product.objects.filter(url=url).first()
            
            if existing_product:
                if update_existing:
                    # Actualizar producto existente
                    for field, value in product_data.items():
                        if hasattr(existing_product, field) and field != 'created_at':
                            setattr(existing_product, field, value)
                    
                    existing_product.save()
                    logger.info(f"Producto actualizado: {existing_product.title}")
                    return existing_product, False
                else:
                    # Retornar producto existente sin modificar
                    logger.debug(f"Producto ya existe: {existing_product.title}")
                    return existing_product, False
            
            # Crear nuevo producto
            product = Product.objects.create(**product_data)
            logger.info(f"Producto creado: {product.title}")
            return product, True
            
        except IntegrityError as e:
            # Manejar carreras de condición (race conditions)
            logger.warning(f"IntegrityError al crear producto, buscando existente: {e}")
            existing_product = Product.objects.filter(url=url).first()
            if existing_product:
                return existing_product, False
            raise e
        except Exception as e:
            logger.error(f"Error creando/actualizando producto: {e}")
            raise e
    
    @staticmethod
    def bulk_create_or_update_products(
        products_data: List[Dict[str, Any]], 
        update_existing: bool = False,
        batch_size: int = 100
    ) -> Dict[str, int]:
        """
        Crear o actualizar múltiples productos en lotes
        
        Args:
            products_data: Lista de datos de productos
            update_existing: Si True, actualiza productos existentes
            batch_size: Tamaño del lote para procesamiento
            
        Returns:
            Dict: Estadísticas del procesamiento
        """
        stats = {
            'created': 0,
            'updated': 0,
            'existing': 0,
            'errors': 0
        }
        
        # Procesar en lotes
        for i in range(0, len(products_data), batch_size):
            batch = products_data[i:i + batch_size]
            
            with transaction.atomic():
                for product_data in batch:
                    try:
                        product, created = ProductManager.create_or_update_product(
                            product_data, update_existing
                        )
                        
                        if created:
                            stats['created'] += 1
                        elif update_existing and not created:
                            stats['updated'] += 1
                        else:
                            stats['existing'] += 1
                            
                    except Exception as e:
                        stats['errors'] += 1
                        logger.error(f"Error procesando producto {product_data.get('title', 'Unknown')}: {e}")
        
        logger.info(f"Procesamiento completado: {stats}")
        return stats
    
    @staticmethod
    def validate_product_data(product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validar y limpiar datos de producto
        
        Args:
            product_data: Datos del producto
            
        Returns:
            Dict: Datos validados y limpiados
        """
        validated_data = {}
        
        # Campos requeridos
        required_fields = ['title', 'price', 'url']
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                raise ValueError(f"Campo requerido faltante: {field}")
            validated_data[field] = product_data[field]
        
        # Validar precio
        price = product_data['price']
        if isinstance(price, str):
            try:
                price = Decimal(price)
            except:
                raise ValueError(f"Precio inválido: {price}")
        
        if price <= 0:
            raise ValueError(f"Precio debe ser positivo: {price}")
        
        validated_data['price'] = price
        
        # Validar URL
        url = product_data['url'].strip()
        if not url.startswith(('http://', 'https://')):
            raise ValueError(f"URL inválida: {url}")
        validated_data['url'] = url
        
        # Validar título
        title = product_data['title'].strip()
        if len(title) < 3:
            raise ValueError(f"Título muy corto: {title}")
        if len(title) > 500:
            title = title[:500]  # Truncar si es muy largo
        validated_data['title'] = title
        
        # Campos opcionales
        optional_fields = {
            'image': str,
            'shipping_time': int,
            'category': str,
            'rating': Decimal,
            'source_platform': str
        }
        
        for field, field_type in optional_fields.items():
            if field in product_data and product_data[field] is not None:
                try:
                    if field_type == Decimal and isinstance(product_data[field], (int, float, str)):
                        validated_data[field] = Decimal(str(product_data[field]))
                    elif field_type == int and isinstance(product_data[field], (str, float)):
                        validated_data[field] = int(float(product_data[field]))
                    elif field_type == str:
                        validated_data[field] = str(product_data[field]).strip()
                    else:
                        validated_data[field] = field_type(product_data[field])
                        
                    # Validaciones específicas
                    if field == 'rating' and validated_data[field] is not None:
                        if not (0 <= validated_data[field] <= 5):
                            raise ValueError(f"Rating debe estar entre 0 y 5: {validated_data[field]}")
                    
                    if field == 'shipping_time' and validated_data[field] is not None:
                        if not (0 <= validated_data[field] <= 365):
                            raise ValueError(f"Tiempo de envío debe estar entre 0 y 365 días: {validated_data[field]}")
                            
                except Exception as e:
                    logger.warning(f"Error validando campo {field}: {e}")
                    # No incluir el campo si la validación falla
        
        return validated_data
    
    @staticmethod
    def deduplicate_products() -> int:
        """
        Eliminar productos duplicados basándose en URL
        
        Returns:
            int: Número de productos duplicados eliminados
        """
        logger.info("Iniciando deduplicación de productos")
        
        duplicates_removed = 0
        
        # Encontrar URLs duplicadas
        from django.db.models import Count
        duplicate_urls = (
            Product.objects
            .values('url')
            .annotate(count=Count('url'))
            .filter(count__gt=1)
        )
        
        for item in duplicate_urls:
            url = item['url']
            count = item['count']
            
            # Obtener todos los productos con esta URL
            products = Product.objects.filter(url=url).order_by('created_at')
            
            # Mantener el más reciente, eliminar los demás
            products_to_delete = products[:-1]  # Todos excepto el último
            
            for product in products_to_delete:
                logger.info(f"Eliminando producto duplicado: {product.title}")
                product.delete()
                duplicates_removed += 1
        
        logger.info(f"Deduplicación completada: {duplicates_removed} productos eliminados")
        return duplicates_removed
    
    @staticmethod
    def get_product_stats() -> Dict[str, Any]:
        """
        Obtener estadísticas de productos
        
        Returns:
            Dict: Estadísticas detalladas
        """
        from django.db.models import Count, Avg, Min, Max
        from datetime import timedelta
        
        total_products = Product.objects.count()
        
        if total_products == 0:
            return {
                'total_products': 0,
                'platforms': [],
                'categories': [],
                'price_stats': {},
                'recent_stats': {}
            }
        
        # Estadísticas de precio
        price_stats = Product.objects.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Plataformas y categorías
        platforms = list(Product.objects.values_list('source_platform', flat=True).distinct())
        categories = list(Product.objects.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct())
        
        # Estadísticas recientes
        now = timezone.now()
        recent_stats = {
            'last_24h': Product.objects.filter(created_at__gte=now - timedelta(hours=24)).count(),
            'last_week': Product.objects.filter(created_at__gte=now - timedelta(days=7)).count(),
            'last_month': Product.objects.filter(created_at__gte=now - timedelta(days=30)).count(),
        }
        
        return {
            'total_products': total_products,
            'platforms': platforms,
            'categories': categories,
            'price_stats': price_stats,
            'recent_stats': recent_stats
        }


# Funciones convenientes
def create_product_safe(product_data: Dict[str, Any]) -> Tuple[Product, bool]:
    """Crear producto con validación y idempotencia"""
    validated_data = ProductManager.validate_product_data(product_data)
    return ProductManager.create_or_update_product(validated_data)


def bulk_import_products(products_data: List[Dict[str, Any]]) -> Dict[str, int]:
    """Importar productos en lote con validación"""
    # Validar todos los productos primero
    validated_products = []
    for product_data in products_data:
        try:
            validated_data = ProductManager.validate_product_data(product_data)
            validated_products.append(validated_data)
        except Exception as e:
            logger.error(f"Producto inválido omitido: {e}")
    
    return ProductManager.bulk_create_or_update_products(validated_products)