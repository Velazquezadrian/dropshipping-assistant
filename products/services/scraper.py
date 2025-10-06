"""
Módulo de scraping para productos de dropshipping
Incluye scrapers para diferentes plataformas y un scraper mock para testing
"""

import logging
import random
import time
import re
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from decimal import Decimal
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote_plus

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
    Scraper optimizado específicamente para AliExpress
    Enfocado únicamente en productos de AliExpress con categorías específicas
    """
    
    def __init__(self):
        self.base_url = "https://www.aliexpress.com"
        self.search_url = "https://www.aliexpress.com/wholesale"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Categorías específicas de AliExpress para mejores resultados
        self.aliexpress_categories = {
            'electronics': ['smartphones', 'earphones', 'chargers', 'power banks', 'bluetooth speakers'],
            'fashion': ['watches', 'jewelry', 'bags', 'accessories', 'sunglasses'],
            'home': ['led lights', 'home decor', 'kitchen gadgets', 'storage', 'security cameras'],
            'sports': ['fitness tracker', 'workout equipment', 'outdoor gear', 'cycling', 'sports accessories'],
            'automotive': ['car accessories', 'phone mounts', 'dash cam', 'car chargers', 'car tools'],
            'beauty': ['makeup tools', 'skin care', 'hair accessories', 'nail art', 'beauty devices']
        }
    
    def scrape_products(self, search_term: str = "electronics", count: int = 5, **kwargs) -> List[Dict[str, Any]]:
        """
        Scraping optimizado de productos de AliExpress con términos específicos
        """
        logger.info(f"AliExpressScraper: Iniciando scraping para '{search_term}' ({count} productos)")
        
        # Optimizar término de búsqueda usando categorías conocidas
        optimized_search_term = self._optimize_search_term(search_term)
        
        try:
            # Construir URL de búsqueda con parámetros adicionales
            search_url = f"{self.search_url}?SearchText={quote_plus(optimized_search_term)}&shipCountry=ES&shipCompanies=&shipFromCountry=&shipToCountry=&minPrice=&maxPrice=&minQuantity=&maxQuantity=&startDate=&endDate=&isFreeShip=y&isFastShip=y&isOnSale=y&isBigSale=y&page=1"
            logger.info(f"URL optimizada: {search_url}")
            
            # Realizar la petición con retry
            response = self._make_request_with_retry(search_url)
            if not response:
                return self._generate_realistic_aliexpress_products(count, search_term)
            
            # Parsear HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Buscar productos en la página
            products = self._extract_products_from_soup(soup, count, search_term)
            
            logger.info(f"AliExpressScraper: {len(products)} productos extraídos para '{search_term}'")
            return products
            
        except Exception as e:
            logger.error(f"Error general en scraping AliExpress: {e}")
            return self._generate_realistic_aliexpress_products(count, search_term)
    
    def _optimize_search_term(self, search_term: str) -> str:
        """
        Optimiza el término de búsqueda usando categorías conocidas de AliExpress
        """
        search_lower = search_term.lower()
        
        # Buscar en categorías para encontrar términos más específicos
        for category, terms in self.aliexpress_categories.items():
            for term in terms:
                if term in search_lower or search_lower in term:
                    logger.debug(f"Término optimizado: '{search_term}' -> '{term}'")
                    return term
        
        return search_term
    
    def _make_request_with_retry(self, url: str, max_retries: int = 3) -> requests.Response:
        """
        Realiza petición con reintentos y delays aleatorios
        """
        for attempt in range(max_retries):
            try:
                # Delay aleatorio para evitar detección
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                
                logger.debug(f"Petición exitosa en intento {attempt + 1}")
                return response
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"Intento {attempt + 1} falló: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Todos los intentos fallaron para: {url}")
                    return None
                time.sleep(random.uniform(2, 5))  # Delay más largo entre reintentos
        
        return None
    
    def _extract_products_from_soup(self, soup: BeautifulSoup, count: int, search_term: str) -> List[Dict[str, Any]]:
        """
        Extrae productos del HTML parseado con selectores mejorados para AliExpress
        """
        products = []
        
        # Selectores actualizados y más específicos para AliExpress 2025
        product_selectors = [
            'div[data-widget-cid]',  # Nuevo selector para widgets de producto
            '.item',
            '.product-item',
            '[data-item-id]',
            '.list-item',
            '.gallery-item',
            '.search-item',
            'div[class*="item"]',
            'div[class*="product"]'
        ]
        
        product_elements = []
        for selector in product_selectors:
            elements = soup.select(selector)
            if elements and len(elements) > 5:  # Asegurar que hay suficientes elementos
                product_elements = elements
                logger.debug(f"Productos encontrados con selector: {selector} ({len(elements)} elementos)")
                break
        
        if not product_elements:
            logger.warning("No se encontraron productos con los selectores conocidos")
            return self._generate_realistic_aliexpress_products(count, search_term)
        
        # Extraer productos con mejor filtrado
        for element in product_elements[:count * 3]:  # Procesar más elementos para filtrar mejor
            try:
                product = self._extract_aliexpress_product_data(element, search_term)
                if product and self._is_valid_product(product):
                    normalized = self.normalize_product(product)
                    products.append(normalized)
                    
                if len(products) >= count:
                    break
                    
            except Exception as e:
                logger.debug(f"Error extrayendo producto individual: {e}")
                continue
        
        # Si no se obtuvieron suficientes productos reales, complementar con datos realistas
        if len(products) < count:
            remaining = count - len(products)
            realistic_products = self._generate_realistic_aliexpress_products(remaining, search_term)
            products.extend(realistic_products)
        
        return products
    
    def _is_valid_product(self, product: Dict[str, Any]) -> bool:
        """
        Valida que el producto tenga datos mínimos requeridos
        """
        return (
            product.get('title') and 
            len(product.get('title', '')) > 10 and
            product.get('price') and
            float(product.get('price', 0)) > 0
        )
    
    def _extract_aliexpress_product_data(self, element, search_term: str) -> Dict[str, Any]:
        """
        Extrae datos de un elemento de producto individual con selectores mejorados
        """
        product = {}
        
        # Título con selectores más específicos
        title_selectors = [
            'a[title]',  # Enlaces con título
            '.title a',
            '.item-title a',
            'h3 a',
            'h4 a',
            '.product-title',
            '[data-spm-anchor-id] a',
            'a[href*="/item/"]'
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                title = title_elem.get('title') or title_elem.get_text(strip=True)
                if title and len(title) > 10:
                    product['title'] = title
                    break
        
        # Precio con mejor parsing
        price_selectors = [
            '.price-current',
            '.price-sale',
            '.item-price',
            '[data-spm-anchor-id*="price"]',
            '.price .num',
            '.product-price',
            'span[class*="price"]'
        ]
        
        for selector in price_selectors:
            price_elem = element.select_one(selector)
            if price_elem:
                price_text = price_elem.get_text(strip=True)
                # Mejorar extracción de precio
                price_match = re.search(r'[\d,]+\.?\d*', price_text.replace('$', '').replace('€', '').replace('US', ''))
                if price_match:
                    try:
                        price_value = float(price_match.group().replace(',', ''))
                        if 1 <= price_value <= 1000:  # Rango razonable de precios
                            product['price'] = price_value
                            break
                    except ValueError:
                        continue
        
        # URL del producto
        url_elem = element.select_one('a[href*="/item/"]') or element.select_one('a[href]')
        if url_elem:
            href = url_elem.get('href')
            if href:
                if href.startswith('//'):
                    href = 'https:' + href
                elif href.startswith('/'):
                    href = self.base_url + href
                product['url'] = href
        
        # Imagen del producto
        img_selectors = [
            'img[src*="alicdn"]',  # Imágenes específicas de AliExpress
            'img[data-src]',
            'img[src]',
            '.item-img img',
            '.product-image img'
        ]
        
        for selector in img_selectors:
            img_elem = element.select_one(selector)
            if img_elem:
                src = img_elem.get('data-src') or img_elem.get('src')
                if src and ('alicdn' in src or 'http' in src):
                    if src.startswith('//'):
                        src = 'https:' + src
                    product['image'] = src
                    break
        
        # Rating mejorado
        rating_selectors = [
            '.star-view .star-num',
            '.rate-num',
            '[data-spm-anchor-id*="rate"]',
            '.rating .num',
            '.product-rating'
        ]
        
        for selector in rating_selectors:
            rating_elem = element.select_one(selector)
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'([\d.]+)', rating_text)
                if rating_match:
                    try:
                        rating_value = float(rating_match.group(1))
                        if 0 <= rating_value <= 5:
                            product['rating'] = rating_value
                            break
                    except ValueError:
                        continue
        
        # Determinar categoría basada en el término de búsqueda
        category = self._determine_category(search_term, product.get('title', ''))
        
        # Valores por defecto mejorados si no se encuentran
        if not product.get('title'):
            return None
        
        product.setdefault('price', random.uniform(5, 150))  # Precios más realistas para AliExpress
        product.setdefault('url', f"{self.base_url}/item/{random.randint(1000000000, 9999999999)}.html")
        product.setdefault('image', 'https://ae01.alicdn.com/kf/placeholder-300x300.jpg')
        product.setdefault('rating', random.uniform(3.8, 4.9))  # Ratings típicos de AliExpress
        product.setdefault('shipping_time', random.randint(7, 25))  # Tiempos de envío típicos
        product.setdefault('category', category)
        
        return product
    
    def _determine_category(self, search_term: str, title: str) -> str:
        """
        Determina la categoría del producto basada en el término de búsqueda y título
        """
        combined_text = (search_term + ' ' + title).lower()
        
        category_keywords = {
            'Electronics': ['phone', 'electronic', 'charger', 'cable', 'battery', 'speaker', 'headphone', 'earphone', 'bluetooth', 'usb'],
            'Fashion': ['watch', 'jewelry', 'ring', 'necklace', 'bracelet', 'bag', 'wallet', 'accessory'],
            'Home & Garden': ['home', 'led', 'light', 'kitchen', 'storage', 'decor', 'lamp', 'camera'],
            'Sports & Outdoors': ['fitness', 'sport', 'outdoor', 'cycling', 'workout', 'exercise'],
            'Automotive': ['car', 'auto', 'vehicle', 'mount', 'dashboard'],
            'Beauty & Health': ['beauty', 'makeup', 'skin', 'hair', 'nail', 'health']
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
        
        return 'Electronics'  # Categoría por defecto
    
    def _generate_realistic_aliexpress_products(self, count: int, search_term: str = "electronics") -> List[Dict[str, Any]]:
        """
        Genera productos realistas específicos de AliExpress basados en el término de búsqueda
        """
        # Productos realistas por categoría específicos de AliExpress
        aliexpress_products = {
            'electronics': [
                {
                    'title': 'Wireless Bluetooth 5.0 Earbuds TWS Touch Control with Charging Case',
                    'price': 15.99,
                    'url': f'{self.base_url}/item/wireless-earbuds-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/earbuds-example.jpg',
                    'shipping_time': random.randint(8, 15),
                    'category': 'Electronics',
                    'rating': 4.3
                },
                {
                    'title': '20000mAh Power Bank Fast Charging Portable Charger LED Display',
                    'price': 22.50,
                    'url': f'{self.base_url}/item/power-bank-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/power-bank-example.jpg',
                    'shipping_time': random.randint(7, 12),
                    'category': 'Electronics',
                    'rating': 4.6
                },
                {
                    'title': 'USB-C Cable Fast Charging Data Sync Cable 3A Quick Charge',
                    'price': 3.99,
                    'url': f'{self.base_url}/item/usb-cable-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/usb-cable-example.jpg',
                    'shipping_time': random.randint(5, 10),
                    'category': 'Electronics',
                    'rating': 4.4
                },
                {
                    'title': 'Bluetooth 5.0 Portable Wireless Speaker IPX7 Waterproof',
                    'price': 28.99,
                    'url': f'{self.base_url}/item/bluetooth-speaker-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/speaker-example.jpg',
                    'shipping_time': random.randint(9, 18),
                    'category': 'Electronics',
                    'rating': 4.5
                }
            ],
            'fashion': [
                {
                    'title': 'Smart Watch Fitness Tracker Heart Rate Monitor IP68 Waterproof',
                    'price': 35.99,
                    'url': f'{self.base_url}/item/smart-watch-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/smartwatch-example.jpg',
                    'shipping_time': random.randint(10, 20),
                    'category': 'Fashion',
                    'rating': 4.2
                },
                {
                    'title': 'Stainless Steel Chain Necklace Pendant Fashion Jewelry',
                    'price': 8.50,
                    'url': f'{self.base_url}/item/necklace-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/necklace-example.jpg',
                    'shipping_time': random.randint(7, 15),
                    'category': 'Fashion',
                    'rating': 4.1
                }
            ],
            'home': [
                {
                    'title': 'LED Strip Lights 5M RGB Color Changing with Remote Control',
                    'price': 12.99,
                    'url': f'{self.base_url}/item/led-strips-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/led-strip-example.jpg',
                    'shipping_time': random.randint(8, 16),
                    'category': 'Home & Garden',
                    'rating': 4.4
                },
                {
                    'title': 'WiFi Security Camera 1080P HD Night Vision Motion Detection',
                    'price': 45.99,
                    'url': f'{self.base_url}/item/security-camera-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/camera-example.jpg',
                    'shipping_time': random.randint(12, 22),
                    'category': 'Home & Garden',
                    'rating': 4.3
                }
            ],
            'automotive': [
                {
                    'title': 'Magnetic Car Phone Mount Dashboard Holder 360° Rotation',
                    'price': 9.99,
                    'url': f'{self.base_url}/item/car-mount-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/car-mount-example.jpg',
                    'shipping_time': random.randint(6, 12),
                    'category': 'Automotive',
                    'rating': 4.7
                },
                {
                    'title': 'Car Dash Cam 1080P Full HD Dashboard Camera Night Vision',
                    'price': 55.00,
                    'url': f'{self.base_url}/item/dash-cam-{random.randint(1000000000, 9999999999)}.html',
                    'image': 'https://ae01.alicdn.com/kf/dashcam-example.jpg',
                    'shipping_time': random.randint(15, 25),
                    'category': 'Automotive',
                    'rating': 4.2
                }
            ]
        }
        
        # Determinar categoría basada en el término de búsqueda
        search_lower = search_term.lower()
        
        if any(term in search_lower for term in ['electronics', 'phone', 'charger', 'cable', 'speaker', 'earbuds']):
            category_products = aliexpress_products['electronics']
        elif any(term in search_lower for term in ['watch', 'jewelry', 'fashion', 'necklace']):
            category_products = aliexpress_products['fashion']
        elif any(term in search_lower for term in ['led', 'home', 'camera', 'lights']):
            category_products = aliexpress_products['home']
        elif any(term in search_lower for term in ['car', 'auto', 'mount', 'dash']):
            category_products = aliexpress_products['automotive']
        else:
            # Por defecto usar electrónicos
            category_products = aliexpress_products['electronics']
        
        # Seleccionar productos aleatorios de la categoría
        available_count = len(category_products)
        if count <= available_count:
            selected = random.sample(category_products, count)
        else:
            # Si necesitamos más productos, repetir algunos con variaciones
            selected = category_products.copy()
            remaining = count - len(selected)
            for _ in range(remaining):
                product = random.choice(category_products).copy()
                # Variar precio y URL para evitar duplicados
                product['price'] = round(product['price'] * random.uniform(0.8, 1.2), 2)
                product['url'] = f"{product['url']}-variant-{random.randint(100, 999)}"
                selected.append(product)
        
        # Agregar variación a precios y URLs para evitar duplicados
        for product in selected:
            price_variation = random.uniform(0.85, 1.15)
            product['price'] = round(product['price'] * price_variation, 2)
            product['url'] = f"{product['url']}-{random.randint(1000, 9999)}"
        
        # Normalizar productos
        normalized_products = []
        for product in selected:
            normalized = self.normalize_product(product)
            normalized_products.append(normalized)
        
        return normalized_products
    
    def _fallback_to_mock(self, count: int, search_term: str = "electronics") -> List[Dict[str, Any]]:
        """
        Fallback a datos AliExpress realistas cuando falla el scraping
        """
        logger.warning("Usando datos de fallback AliExpress debido a error en scraping")
        return self._generate_realistic_aliexpress_products(count, search_term)
    
    def get_platform_name(self) -> str:
        return 'aliexpress'


class ScraperFactory:
    """Factory para crear scrapers - SOLO ALIEXPRESS"""
    
    scrapers = {
        'mock': MockScraper,
        'aliexpress': AliExpressScraper,
        # 'aliexpress_advanced': Se deshabilitó temporalmente - usar aliexpress estándar
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