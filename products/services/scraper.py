"""
Módulo de scraping para productos de dropshipping
Incluye scrapers para diferentes plataformas y un scraper mock para testing
"""

import logging
import random
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from decimal import Decimal

logger = logging.getLogger('products')


class BaseScraper(ABC):
    """Clase base para todos los scrapers"""
    
    @abstractmethod
    def scrape_products(self, **kwargs) -> List[Dict[str, Any]]:
        """
        Método abstracto para scraping de productos
        
        Returns:
            List[Dict]: Lista de productos con formato estándar
        """
        pass
    
    def normalize_product(self, raw_product: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normaliza los datos del producto a formato estándar
        
        Args:
            raw_product: Datos del producto sin procesar
            
        Returns:
            Dict: Producto normalizado
        """
        return {
            'title': str(raw_product.get('title', '')).strip(),
            'price': self._parse_price(raw_product.get('price')),
            'url': str(raw_product.get('url', '')).strip(),
            'image': str(raw_product.get('image', '')).strip(),
            'shipping_time': self._parse_shipping_time(raw_product.get('shipping_time')),
            'category': str(raw_product.get('category', '')).strip(),
            'rating': self._parse_rating(raw_product.get('rating')),
            'source_platform': self.get_platform_name()
        }
    
    def _parse_price(self, price_data) -> Decimal:
        """Parsea el precio a Decimal"""
        if isinstance(price_data, (int, float)):
            return Decimal(str(price_data))
        if isinstance(price_data, str):
            # Remover símbolos de moneda y espacios
            clean_price = ''.join(c for c in price_data if c.isdigit() or c == '.')
            return Decimal(clean_price) if clean_price else Decimal('0.00')
        return Decimal('0.00')
    
    def _parse_shipping_time(self, shipping_data) -> int:
        """Parsea el tiempo de envío a entero"""
        if isinstance(shipping_data, int):
            return shipping_data
        if isinstance(shipping_data, str):
            # Extraer números del string
            numbers = ''.join(c for c in shipping_data if c.isdigit())
            return int(numbers) if numbers else 30
        return 30  # Valor por defecto
    
    def _parse_rating(self, rating_data) -> Decimal:
        """Parsea la calificación a Decimal"""
        if isinstance(rating_data, (int, float)):
            return Decimal(str(min(max(rating_data, 0), 5)))  # Entre 0 y 5
        if isinstance(rating_data, str):
            try:
                rating = float(rating_data)
                return Decimal(str(min(max(rating, 0), 5)))
            except ValueError:
                return Decimal('0.00')
        return Decimal('0.00')
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma"""
        pass


class MockScraper(BaseScraper):
    """Scraper mock para testing y desarrollo"""
    
    def __init__(self):
        self.mock_products = [
            {
                'title': 'Smartphone Android 128GB',
                'price': 299.99,
                'url': 'https://example-aliexpress.com/item/smartphone-android-128gb-1',
                'image': 'https://example.com/images/smartphone1.jpg',
                'shipping_time': 15,
                'category': 'Electronics',
                'rating': 4.5
            },
            {
                'title': 'Wireless Bluetooth Headphones',
                'price': 49.99,
                'url': 'https://example-aliexpress.com/item/wireless-bluetooth-headphones-2',
                'image': 'https://example.com/images/headphones1.jpg',
                'shipping_time': 10,
                'category': 'Electronics',
                'rating': 4.2
            },
            {
                'title': 'LED Desk Lamp with USB Charging',
                'price': 25.99,
                'url': 'https://example-aliexpress.com/item/led-desk-lamp-usb-3',
                'image': 'https://example.com/images/lamp1.jpg',
                'shipping_time': 20,
                'category': 'Home & Garden',
                'rating': 4.7
            },
            {
                'title': 'Fitness Tracker Smart Watch',
                'price': 89.99,
                'url': 'https://example-aliexpress.com/item/fitness-tracker-watch-4',
                'image': 'https://example.com/images/watch1.jpg',
                'shipping_time': 12,
                'category': 'Sports & Outdoors',
                'rating': 4.3
            },
            {
                'title': 'Portable Power Bank 20000mAh',
                'price': 35.99,
                'url': 'https://example-aliexpress.com/item/power-bank-20000mah-5',
                'image': 'https://example.com/images/powerbank1.jpg',
                'shipping_time': 18,
                'category': 'Electronics',
                'rating': 4.6
            },
            {
                'title': 'Ergonomic Office Chair',
                'price': 159.99,
                'url': 'https://example-aliexpress.com/item/office-chair-ergonomic-6',
                'image': 'https://example.com/images/chair1.jpg',
                'shipping_time': 25,
                'category': 'Office',
                'rating': 4.4
            }
        ]
    
    def scrape_products(self, count: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Simula el scraping retornando productos mock
        
        Args:
            count: Número de productos a retornar
            
        Returns:
            List[Dict]: Lista de productos normalizados
        """
        logger.info(f"MockScraper: Generando {count} productos mock")
        
        # Seleccionar productos aleatorios
        selected_products = random.sample(self.mock_products, min(count, len(self.mock_products)))
        
        # Agregar variación a los URLs para evitar duplicados en la DB
        for i, product in enumerate(selected_products):
            product = product.copy()
            product['url'] = f"{product['url']}-{random.randint(1000, 9999)}"
            # Pequeña variación en el precio
            price_variation = random.uniform(0.9, 1.1)
            product['price'] = round(product['price'] * price_variation, 2)
            selected_products[i] = product
        
        # Normalizar productos
        normalized_products = []
        for product in selected_products:
            try:
                normalized = self.normalize_product(product)
                normalized_products.append(normalized)
                logger.debug(f"Producto normalizado: {normalized['title']}")
            except Exception as e:
                logger.error(f"Error normalizando producto {product}: {e}")
        
        logger.info(f"MockScraper: {len(normalized_products)} productos listos")
        return normalized_products
    
    def get_platform_name(self) -> str:
        return 'mock_aliexpress'


class AliExpressScraper(BaseScraper):
    """
    Scraper para AliExpress (implementación básica)
    En producción, esto requeriría un scraper más robusto con manejo de anti-bot
    """
    
    def __init__(self):
        self.base_url = "https://www.aliexpress.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def scrape_products(self, search_term: str = "electronics", **kwargs) -> List[Dict[str, Any]]:
        """
        Implementación básica de scraping de AliExpress
        NOTA: Esta es una implementación simplificada. En producción necesitaría:
        - Manejo de cookies y sesiones
        - Rotación de proxies
        - Manejo de captcha
        - Rate limiting
        """
        logger.warning("AliExpressScraper: Implementación básica, usando MockScraper por ahora")
        
        # Por ahora, delegamos al MockScraper para evitar problemas de anti-bot
        mock_scraper = MockScraper()
        return mock_scraper.scrape_products(**kwargs)
    
    def get_platform_name(self) -> str:
        return 'aliexpress'


class ScraperFactory:
    """Factory para crear scrapers según la plataforma"""
    
    scrapers = {
        'mock': MockScraper,
        'aliexpress': AliExpressScraper,
    }
    
    @classmethod
    def get_scraper(cls, platform: str) -> BaseScraper:
        """
        Obtiene un scraper según la plataforma
        
        Args:
            platform: Nombre de la plataforma
            
        Returns:
            BaseScraper: Instancia del scraper
        """
        scraper_class = cls.scrapers.get(platform.lower())
        if not scraper_class:
            logger.warning(f"Plataforma {platform} no encontrada, usando MockScraper")
            scraper_class = MockScraper
        
        return scraper_class()
    
    @classmethod
    def get_available_platforms(cls) -> List[str]:
        """Retorna lista de plataformas disponibles"""
        return list(cls.scrapers.keys())


def scrape_all_platforms(count_per_platform: int = 5) -> List[Dict[str, Any]]:
    """
    Scraping de todas las plataformas disponibles
    
    Args:
        count_per_platform: Número de productos por plataforma
        
    Returns:
        List[Dict]: Lista consolidada de productos
    """
    all_products = []
    platforms = ScraperFactory.get_available_platforms()
    
    logger.info(f"Iniciando scraping de {len(platforms)} plataformas")
    
    for platform in platforms:
        try:
            scraper = ScraperFactory.get_scraper(platform)
            products = scraper.scrape_products(count=count_per_platform)
            all_products.extend(products)
            logger.info(f"Scrapeados {len(products)} productos de {platform}")
        except Exception as e:
            logger.error(f"Error scrapeando {platform}: {e}")
    
    logger.info(f"Scraping completado: {len(all_products)} productos totales")
    return all_products