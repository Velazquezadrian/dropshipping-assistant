"""
Tests para la aplicación de productos dropshipping
"""

import json
from decimal import Decimal
from unittest.mock import patch, MagicMock
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Product
from products.services.scraper import MockScraper, ScraperFactory, scrape_all_platforms
from products.services.filters import ProductFilter, create_filter_from_params
from products.services.product_manager import ProductManager, create_product_safe, bulk_import_products
from products.services.notifications import TelegramNotificationService, DiscordNotificationService


class ProductModelTest(TestCase):
    """Tests para el modelo Product"""
    
    def setUp(self):
        self.product_data = {
            'title': 'Test Product',
            'price': Decimal('29.99'),
            'url': 'https://example.com/test-product',
            'image': 'https://example.com/image.jpg',
            'shipping_time': 15,
            'category': 'Electronics',
            'rating': Decimal('4.5'),
            'source_platform': 'test_platform'
        }
    
    def test_create_product(self):
        """Test creación de producto"""
        product = Product.objects.create(**self.product_data)
        
        self.assertEqual(product.title, 'Test Product')
        self.assertEqual(product.price, Decimal('29.99'))
        self.assertEqual(product.url, 'https://example.com/test-product')
        self.assertTrue(product.is_recently_added())
    
    def test_product_str(self):
        """Test representación string del producto"""
        product = Product.objects.create(**self.product_data)
        expected_str = f"{product.title} - ${product.price}"
        self.assertEqual(str(product), expected_str)
    
    def test_unique_url_constraint(self):
        """Test que la URL debe ser única"""
        Product.objects.create(**self.product_data)
        
        # Intentar crear otro producto con la misma URL debería fallar
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            Product.objects.create(**self.product_data)
    
    def test_is_recently_added(self):
        """Test método is_recently_added"""
        product = Product.objects.create(**self.product_data)
        self.assertTrue(product.is_recently_added())
        
        # Producto más antiguo
        old_product_data = self.product_data.copy()
        old_product_data['url'] = 'https://example.com/old-product'
        old_product = Product.objects.create(**old_product_data)
        
        # Modificar created_at para simular producto antiguo
        from datetime import timedelta
        old_product.created_at = timezone.now() - timedelta(hours=25)
        old_product.save()
        
        self.assertFalse(old_product.is_recently_added())


class ScraperTest(TestCase):
    """Tests para el módulo scraper"""
    
    def test_mock_scraper(self):
        """Test MockScraper"""
        scraper = MockScraper()
        products = scraper.scrape_products(count=3)
        
        self.assertEqual(len(products), 3)
        
        for product in products:
            self.assertIn('title', product)
            self.assertIn('price', product)
            self.assertIn('url', product)
            self.assertIn('source_platform', product)
            self.assertEqual(product['source_platform'], 'mock_aliexpress')
    
    def test_scraper_factory(self):
        """Test ScraperFactory"""
        # Test obtener scraper mock
        scraper = ScraperFactory.get_scraper('mock')
        self.assertIsInstance(scraper, MockScraper)
        
        # Test plataforma inexistente debería retornar MockScraper
        scraper = ScraperFactory.get_scraper('inexistente')
        self.assertIsInstance(scraper, MockScraper)
        
        # Test plataformas disponibles
        platforms = ScraperFactory.get_available_platforms()
        self.assertIn('mock', platforms)
        self.assertIn('aliexpress', platforms)
    
    def test_scrape_all_platforms(self):
        """Test scraping de todas las plataformas"""
        products = scrape_all_platforms(count_per_platform=2)
        
        # Debería haber productos de múltiples plataformas
        self.assertGreater(len(products), 0)
        
        # Verificar estructura de productos
        for product in products:
            self.assertIn('title', product)
            self.assertIn('price', product)
            self.assertIn('url', product)
            self.assertIsInstance(product['price'], Decimal)


class FilterTest(TestCase):
    """Tests para el sistema de filtros"""
    
    def setUp(self):
        # Crear productos de prueba
        self.products = [
            Product.objects.create(
                title='Smartphone Android',
                price=Decimal('299.99'),
                url='https://example.com/smartphone',
                category='Electronics',
                rating=Decimal('4.5'),
                shipping_time=10
            ),
            Product.objects.create(
                title='Wireless Headphones',
                price=Decimal('49.99'),
                url='https://example.com/headphones',
                category='Electronics', 
                rating=Decimal('4.2'),
                shipping_time=15
            ),
            Product.objects.create(
                title='Office Chair',
                price=Decimal('159.99'),
                url='https://example.com/chair',
                category='Office',
                rating=Decimal('4.7'),
                shipping_time=25
            )
        ]
    
    def test_price_filter(self):
        """Test filtro de precio"""
        product_filter = ProductFilter()
        product_filter.add_price_filter(min_price=50, max_price=200)
        
        filtered_queryset = product_filter.filter_queryset(Product.objects.all())
        
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset.first().title, 'Office Chair')
    
    def test_keyword_filter(self):
        """Test filtro de palabras clave"""
        product_filter = ProductFilter()
        product_filter.add_keyword_filter(['smartphone', 'android'])
        
        filtered_queryset = product_filter.filter_queryset(Product.objects.all())
        
        self.assertEqual(filtered_queryset.count(), 1)
        self.assertEqual(filtered_queryset.first().title, 'Smartphone Android')
    
    def test_shipping_time_filter(self):
        """Test filtro de tiempo de envío"""
        product_filter = ProductFilter()
        product_filter.add_shipping_time_filter(max_shipping_days=20)
        
        filtered_queryset = product_filter.filter_queryset(Product.objects.all())
        
        self.assertEqual(filtered_queryset.count(), 2)
        # No debería incluir la silla que tiene 25 días de envío
    
    def test_create_filter_from_params(self):
        """Test creación de filtro desde parámetros"""
        params = {
            'min_price': '50',
            'max_price': '200',
            'keywords': 'electronics,smartphone',
            'max_shipping_days': '20'
        }
        
        product_filter = create_filter_from_params(**params)
        
        self.assertEqual(len(product_filter.filters), 3)  # precio, keywords, shipping
        
        # Verificar que los filtros están configurados correctamente
        filter_summary = product_filter.get_filter_summary()
        self.assertIn('price', filter_summary['filter_types'])
        self.assertIn('keywords', filter_summary['filter_types'])
        self.assertIn('shipping_time', filter_summary['filter_types'])


class ProductManagerTest(TransactionTestCase):
    """Tests para el ProductManager"""
    
    def setUp(self):
        self.product_data = {
            'title': 'Test Product Manager',
            'price': '39.99',
            'url': 'https://example.com/test-manager',
            'category': 'Test Category'
        }
    
    def test_validate_product_data(self):
        """Test validación de datos de producto"""
        validated_data = ProductManager.validate_product_data(self.product_data)
        
        self.assertEqual(validated_data['title'], 'Test Product Manager')
        self.assertEqual(validated_data['price'], Decimal('39.99'))
        self.assertEqual(validated_data['url'], 'https://example.com/test-manager')
    
    def test_validate_invalid_data(self):
        """Test validación con datos inválidos"""
        invalid_data = {
            'title': '',  # Título vacío
            'price': '-10',  # Precio negativo
            'url': 'invalid-url'  # URL inválida
        }
        
        with self.assertRaises(ValueError):
            ProductManager.validate_product_data(invalid_data)
    
    def test_create_or_update_product(self):
        """Test crear o actualizar producto"""
        # Crear producto
        product, created = ProductManager.create_or_update_product(self.product_data)
        
        self.assertTrue(created)
        self.assertEqual(product.title, 'Test Product Manager')
        
        # Intentar crear el mismo producto (debería retornar existente)
        product2, created2 = ProductManager.create_or_update_product(self.product_data)
        
        self.assertFalse(created2)
        self.assertEqual(product.id, product2.id)
    
    def test_bulk_import_products(self):
        """Test importación en lote"""
        products_data = [
            {
                'title': 'Product 1',
                'price': '19.99',
                'url': 'https://example.com/product1'
            },
            {
                'title': 'Product 2', 
                'price': '29.99',
                'url': 'https://example.com/product2'
            },
            {
                'title': 'Product 1',  # Duplicado
                'price': '19.99',
                'url': 'https://example.com/product1'
            }
        ]
        
        stats = bulk_import_products(products_data)
        
        self.assertEqual(stats['created'], 2)
        self.assertEqual(stats['existing'], 1)
        self.assertEqual(Product.objects.count(), 2)


class APITest(APITestCase):
    """Tests para la API REST"""
    
    def setUp(self):
        # Crear productos de prueba
        self.product1 = Product.objects.create(
            title='API Test Product 1',
            price=Decimal('25.99'),
            url='https://example.com/api-test-1',
            category='Electronics'
        )
        self.product2 = Product.objects.create(
            title='API Test Product 2',
            price=Decimal('45.99'),
            url='https://example.com/api-test-2',
            category='Home'
        )
    
    def test_list_products(self):
        """Test listado de productos"""
        url = reverse('product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_filter_products_by_price(self):
        """Test filtrado por precio"""
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': '30'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'API Test Product 2')
    
    def test_search_products(self):
        """Test búsqueda de productos"""
        url = reverse('product-list')
        response = self.client.get(url, {'search': 'Electronics'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_stats_endpoint(self):
        """Test endpoint de estadísticas"""
        url = reverse('product-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_products', response.data)
        self.assertEqual(response.data['total_products'], 2)
    
    def test_health_check_endpoint(self):
        """Test endpoint de health check"""
        url = reverse('health-status')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertIn('products_count', response.data)
    
    def test_simple_health_check(self):
        """Test health check simple"""
        url = '/health/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')


class NotificationTest(TestCase):
    """Tests para el sistema de notificaciones"""
    
    def setUp(self):
        self.product = Product.objects.create(
            title='Notification Test Product',
            price=Decimal('19.99'),
            url='https://example.com/notification-test',
            category='Test'
        )
    
    @patch('requests.post')
    def test_telegram_notification(self, mock_post):
        """Test notificación por Telegram"""
        # Mock respuesta exitosa
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Configurar servicio
        from products.services.notifications import TelegramNotificationService
        service = TelegramNotificationService()
        service.bot_token = 'test_token'
        service.chat_id = 'test_chat'
        service.enabled = True
        
        # Enviar notificación
        message = service.format_product_message(self.product)
        result = service.send_notification(message)
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_discord_notification(self, mock_post):
        """Test notificación por Discord"""
        # Mock respuesta exitosa
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        # Configurar servicio
        from products.services.notifications import DiscordNotificationService
        service = DiscordNotificationService()
        service.webhook_url = 'https://discord.com/test-webhook'
        service.enabled = True
        
        # Enviar notificación
        message = service.format_product_message(self.product)
        result = service.send_notification(message)
        
        self.assertTrue(result)
        mock_post.assert_called_once()
    
    def test_notification_manager(self):
        """Test gestor de notificaciones"""
        from products.services.notifications import NotificationManager
        
        manager = NotificationManager()
        
        # Test con servicios no configurados
        results = manager.notify_new_product(self.product)
        
        # Debería retornar diccionario vacío si no hay servicios configurados
        self.assertIsInstance(results, dict)


class IntegrationTest(TransactionTestCase):
    """Tests de integración"""
    
    def test_full_scraping_workflow(self):
        """Test workflow completo de scraping"""
        # 1. Ejecutar scraper
        from products.services.scraper import MockScraper
        scraper = MockScraper()
        products_data = scraper.scrape_products(count=3)
        
        # 2. Importar productos
        stats = bulk_import_products(products_data)
        
        # 3. Verificar que se crearon
        self.assertEqual(stats['created'], 3)
        self.assertEqual(Product.objects.count(), 3)
        
        # 4. Ejecutar scraper nuevamente (debería detectar duplicados)
        products_data2 = scraper.scrape_products(count=3)
        stats2 = bulk_import_products(products_data2)
        
        # No deberían crear productos nuevos (URLs diferentes por randomización)
        # Pero al menos debería manejar la situación sin errores
        self.assertEqual(stats2['errors'], 0)
    
    def test_api_with_filters(self):
        """Test API con filtros"""
        # Crear productos con datos específicos
        Product.objects.create(
            title='Expensive Phone',
            price=Decimal('999.99'),
            url='https://example.com/expensive-phone',
            category='Electronics',
            shipping_time=5
        )
        Product.objects.create(
            title='Cheap Accessory',
            price=Decimal('9.99'),
            url='https://example.com/cheap-accessory',
            category='Accessories',
            shipping_time=30
        )
        
        # Test filtro por precio
        from django.urls import reverse
        url = reverse('product-list')
        response = self.client.get(url, {
            'min_price': '100',
            'max_shipping_days': '10'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Expensive Phone')
