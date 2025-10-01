"""
Módulo de filtrado para productos de dropshipping
Proporciona filtros flexibles para productos basados en diferentes criterios
"""

import logging
from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db.models import QuerySet
from products.models import Product

logger = logging.getLogger('products')


class ProductFilter:
    """Clase para filtrar productos basado en diferentes criterios"""
    
    def __init__(self):
        self.filters = []
    
    def add_price_filter(self, min_price: Optional[float] = None, max_price: Optional[float] = None):
        """
        Agregar filtro de precio
        
        Args:
            min_price: Precio mínimo
            max_price: Precio máximo
        """
        if min_price is not None or max_price is not None:
            self.filters.append({
                'type': 'price',
                'min_price': Decimal(str(min_price)) if min_price is not None else None,
                'max_price': Decimal(str(max_price)) if max_price is not None else None
            })
        return self
    
    def add_keyword_filter(self, keywords: List[str], search_in_title: bool = True, search_in_category: bool = True):
        """
        Agregar filtro de palabras clave
        
        Args:
            keywords: Lista de palabras clave a buscar
            search_in_title: Buscar en el título
            search_in_category: Buscar en la categoría
        """
        if keywords:
            self.filters.append({
                'type': 'keywords',
                'keywords': [keyword.lower().strip() for keyword in keywords],
                'search_in_title': search_in_title,
                'search_in_category': search_in_category
            })
        return self
    
    def add_shipping_time_filter(self, max_shipping_days: Optional[int] = None):
        """
        Agregar filtro de tiempo de envío
        
        Args:
            max_shipping_days: Máximo número de días de envío
        """
        if max_shipping_days is not None:
            self.filters.append({
                'type': 'shipping_time',
                'max_days': max_shipping_days
            })
        return self
    
    def add_rating_filter(self, min_rating: Optional[float] = None):
        """
        Agregar filtro de calificación
        
        Args:
            min_rating: Calificación mínima
        """
        if min_rating is not None:
            self.filters.append({
                'type': 'rating',
                'min_rating': Decimal(str(min_rating))
            })
        return self
    
    def add_platform_filter(self, platforms: List[str]):
        """
        Agregar filtro de plataforma
        
        Args:
            platforms: Lista de plataformas permitidas
        """
        if platforms:
            self.filters.append({
                'type': 'platform',
                'platforms': [platform.lower().strip() for platform in platforms]
            })
        return self
    
    def add_category_filter(self, categories: List[str]):
        """
        Agregar filtro de categoría
        
        Args:
            categories: Lista de categorías permitidas
        """
        if categories:
            self.filters.append({
                'type': 'category',
                'categories': [category.lower().strip() for category in categories]
            })
        return self
    
    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        """
        Aplicar filtros a un QuerySet de Django
        
        Args:
            queryset: QuerySet a filtrar
            
        Returns:
            QuerySet: QuerySet filtrado
        """
        for filter_config in self.filters:
            queryset = self._apply_queryset_filter(queryset, filter_config)
        
        logger.info(f"Filtros aplicados al QuerySet. Resultados: {queryset.count()}")
        return queryset
    
    def filter_product_list(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Aplicar filtros a una lista de productos (diccionarios)
        
        Args:
            products: Lista de productos a filtrar
            
        Returns:
            List[Dict]: Lista filtrada de productos
        """
        filtered_products = products.copy()
        
        for filter_config in self.filters:
            filtered_products = [
                product for product in filtered_products
                if self._matches_filter(product, filter_config)
            ]
        
        logger.info(f"Filtros aplicados a lista. Productos originales: {len(products)}, filtrados: {len(filtered_products)}")
        return filtered_products
    
    def _apply_queryset_filter(self, queryset: QuerySet, filter_config: Dict[str, Any]) -> QuerySet:
        """Aplicar un filtro específico al QuerySet"""
        filter_type = filter_config['type']
        
        if filter_type == 'price':
            if filter_config['min_price'] is not None:
                queryset = queryset.filter(price__gte=filter_config['min_price'])
            if filter_config['max_price'] is not None:
                queryset = queryset.filter(price__lte=filter_config['max_price'])
        
        elif filter_type == 'keywords':
            keywords = filter_config['keywords']
            search_in_title = filter_config['search_in_title']
            search_in_category = filter_config['search_in_category']
            
            if search_in_title and search_in_category:
                # Buscar en título O categoría
                from django.db.models import Q
                keyword_q = Q()
                for keyword in keywords:
                    keyword_q |= Q(title__icontains=keyword) | Q(category__icontains=keyword)
                queryset = queryset.filter(keyword_q)
            elif search_in_title:
                from django.db.models import Q
                keyword_q = Q()
                for keyword in keywords:
                    keyword_q |= Q(title__icontains=keyword)
                queryset = queryset.filter(keyword_q)
            elif search_in_category:
                from django.db.models import Q
                keyword_q = Q()
                for keyword in keywords:
                    keyword_q |= Q(category__icontains=keyword)
                queryset = queryset.filter(keyword_q)
        
        elif filter_type == 'shipping_time':
            queryset = queryset.filter(shipping_time__lte=filter_config['max_days'])
        
        elif filter_type == 'rating':
            queryset = queryset.filter(rating__gte=filter_config['min_rating'])
        
        elif filter_type == 'platform':
            queryset = queryset.filter(source_platform__in=filter_config['platforms'])
        
        elif filter_type == 'category':
            from django.db.models import Q
            category_q = Q()
            for category in filter_config['categories']:
                category_q |= Q(category__icontains=category)
            queryset = queryset.filter(category_q)
        
        return queryset
    
    def _matches_filter(self, product: Dict[str, Any], filter_config: Dict[str, Any]) -> bool:
        """Verificar si un producto coincide con un filtro específico"""
        filter_type = filter_config['type']
        
        if filter_type == 'price':
            price = Decimal(str(product.get('price', 0)))
            
            if filter_config['min_price'] is not None and price < filter_config['min_price']:
                return False
            if filter_config['max_price'] is not None and price > filter_config['max_price']:
                return False
        
        elif filter_type == 'keywords':
            keywords = filter_config['keywords']
            search_in_title = filter_config['search_in_title']
            search_in_category = filter_config['search_in_category']
            
            title = product.get('title', '').lower()
            category = product.get('category', '').lower()
            
            found_keyword = False
            for keyword in keywords:
                if search_in_title and keyword in title:
                    found_keyword = True
                    break
                if search_in_category and keyword in category:
                    found_keyword = True
                    break
            
            if not found_keyword:
                return False
        
        elif filter_type == 'shipping_time':
            shipping_time = product.get('shipping_time', 999)
            if shipping_time > filter_config['max_days']:
                return False
        
        elif filter_type == 'rating':
            rating = Decimal(str(product.get('rating', 0)))
            if rating < filter_config['min_rating']:
                return False
        
        elif filter_type == 'platform':
            platform = product.get('source_platform', '').lower()
            if platform not in filter_config['platforms']:
                return False
        
        elif filter_type == 'category':
            category = product.get('category', '').lower()
            found_category = False
            for allowed_category in filter_config['categories']:
                if allowed_category in category:
                    found_category = True
                    break
            if not found_category:
                return False
        
        return True
    
    def clear_filters(self):
        """Limpiar todos los filtros"""
        self.filters = []
        return self
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """Obtener resumen de los filtros aplicados"""
        summary = {
            'total_filters': len(self.filters),
            'filter_types': [f['type'] for f in self.filters],
            'filters': self.filters
        }
        return summary


def create_filter_from_params(**params) -> ProductFilter:
    """
    Crear un filtro basado en parámetros de query
    
    Args:
        **params: Parámetros de filtrado
        
    Returns:
        ProductFilter: Filtro configurado
    """
    product_filter = ProductFilter()
    
    # Filtro de precio
    min_price = params.get('min_price')
    max_price = params.get('max_price')
    if min_price is not None or max_price is not None:
        try:
            min_price = float(min_price) if min_price else None
            max_price = float(max_price) if max_price else None
            product_filter.add_price_filter(min_price, max_price)
        except (ValueError, TypeError):
            logger.warning(f"Precio inválido: min_price={min_price}, max_price={max_price}")
    
    # Filtro de palabras clave
    keywords = params.get('keywords')
    if keywords:
        if isinstance(keywords, str):
            keywords = [k.strip() for k in keywords.split(',') if k.strip()]
        product_filter.add_keyword_filter(keywords)
    
    # Filtro de tiempo de envío
    max_shipping = params.get('max_shipping_days')
    if max_shipping is not None:
        try:
            max_shipping = int(max_shipping)
            product_filter.add_shipping_time_filter(max_shipping)
        except (ValueError, TypeError):
            logger.warning(f"Tiempo de envío inválido: {max_shipping}")
    
    # Filtro de calificación
    min_rating = params.get('min_rating')
    if min_rating is not None:
        try:
            min_rating = float(min_rating)
            product_filter.add_rating_filter(min_rating)
        except (ValueError, TypeError):
            logger.warning(f"Calificación inválida: {min_rating}")
    
    # Filtro de plataforma
    platforms = params.get('platforms')
    if platforms:
        if isinstance(platforms, str):
            platforms = [p.strip() for p in platforms.split(',') if p.strip()]
        product_filter.add_platform_filter(platforms)
    
    # Filtro de categoría
    categories = params.get('categories')
    if categories:
        if isinstance(categories, str):
            categories = [c.strip() for c in categories.split(',') if c.strip()]
        product_filter.add_category_filter(categories)
    
    logger.info(f"Filtro creado con {len(product_filter.filters)} reglas")
    return product_filter