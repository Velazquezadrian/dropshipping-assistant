"""
Script de testing para el módulo de scraping
Prueba todas las funcionalidades: MockScraper, AliExpressScraper, normalización y factory
"""

import sys
import os
import logging
from typing import List, Dict, Any
from decimal import Decimal

# Agregar el directorio de products al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'products'))

from products.services.scraper import (
    MockScraper, 
    AliExpressScraper, 
    ScraperFactory, 
    scrape_all_platforms
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger('test_scraper')


def validate_product_structure(product: Dict[str, Any]) -> bool:
    """
    Valida que un producto tenga la estructura esperada
    """
    required_fields = ['title', 'price', 'url', 'image', 'shipping_time', 'category', 'rating', 'source_platform']
    
    # Verificar campos requeridos
    for field in required_fields:
        if field not in product:
            logger.error(f"Campo faltante: {field}")
            return False
    
    # Verificar tipos de datos
    validations = [
        (isinstance(product['title'], str), "title debe ser string"),
        (isinstance(product['price'], Decimal), "price debe ser Decimal"),
        (isinstance(product['url'], str), "url debe ser string"),
        (isinstance(product['image'], str), "image debe ser string"),
        (isinstance(product['shipping_time'], int), "shipping_time debe ser int"),
        (isinstance(product['category'], str), "category debe ser string"),
        (isinstance(product['rating'], Decimal), "rating debe ser Decimal"),
        (isinstance(product['source_platform'], str), "source_platform debe ser string"),
        (len(product['title']) > 0, "title no puede estar vacío"),
        (product['price'] >= 0, "price debe ser >= 0"),
        (len(product['url']) > 0, "url no puede estar vacía"),
        (0 <= product['rating'] <= 5, "rating debe estar entre 0 y 5"),
        (product['shipping_time'] > 0, "shipping_time debe ser > 0")
    ]
    
    for is_valid, error_msg in validations:
        if not is_valid:
            logger.error(f"Validación fallida: {error_msg}")
            return False
    
    return True


def test_mock_scraper():
    """
    Prueba el MockScraper
    """
    logger.info("=== TESTING MOCK SCRAPER ===")
    
    scraper = MockScraper()
    
    # Test básico
    products = scraper.scrape_products(count=3)
    logger.info(f"MockScraper retornó {len(products)} productos")
    
    # Validar productos
    for i, product in enumerate(products):
        logger.info(f"Producto {i+1}: {product['title']} - ${product['price']} - {product['source_platform']}")
        if not validate_product_structure(product):
            logger.error(f"Producto {i+1} falló validación")
            return False
    
    # Test con diferentes cantidades
    test_counts = [1, 5, 10]
    for count in test_counts:
        products = scraper.scrape_products(count=count)
        expected = min(count, 6)  # MockScraper tiene 6 productos base
        if len(products) != expected:
            logger.error(f"Se esperaban {expected} productos, se obtuvieron {len(products)}")
            return False
        logger.info(f"✓ Test con count={count} exitoso")
    
    logger.info("✓ MockScraper PASSED")
    return True


def test_aliexpress_scraper():
    """
    Prueba el AliExpressScraper
    """
    logger.info("=== TESTING ALIEXPRESS SCRAPER ===")
    
    scraper = AliExpressScraper()
    
    # Test con diferentes términos de búsqueda
    search_terms = ['electronics', 'fashion', 'home', 'automotive']
    
    for search_term in search_terms:
        logger.info(f"Testing búsqueda: {search_term}")
        products = scraper.scrape_products(search_term=search_term, count=3)
        
        if len(products) == 0:
            logger.error(f"No se obtuvieron productos para '{search_term}'")
            return False
        
        logger.info(f"AliExpressScraper retornó {len(products)} productos para '{search_term}'")
        
        # Validar productos
        for i, product in enumerate(products):
            logger.info(f"  {i+1}. {product['title'][:50]}... - ${product['price']} - {product['category']}")
            if not validate_product_structure(product):
                logger.error(f"Producto {i+1} de '{search_term}' falló validación")
                return False
            
            # Verificar que sea de AliExpress
            if product['source_platform'] != 'aliexpress':
                logger.error(f"source_platform debe ser 'aliexpress', se obtuvo '{product['source_platform']}'")
                return False
    
    # Test de optimización de términos de búsqueda
    logger.info("Testing optimización de términos...")
    optimized = scraper._optimize_search_term('phone')
    logger.info(f"'phone' optimizado a: '{optimized}'")
    
    # Test de categorización
    category = scraper._determine_category('electronics', 'bluetooth earphones')
    logger.info(f"Categoría determinada: {category}")
    
    logger.info("✓ AliExpressScraper PASSED")
    return True


def test_scraper_factory():
    """
    Prueba el ScraperFactory
    """
    logger.info("=== TESTING SCRAPER FACTORY ===")
    
    # Test de plataformas disponibles
    platforms = ScraperFactory.get_available_platforms()
    logger.info(f"Plataformas disponibles: {platforms}")
    
    expected_platforms = ['mock', 'aliexpress']
    for platform in expected_platforms:
        if platform not in platforms:
            logger.error(f"Plataforma esperada '{platform}' no encontrada")
            return False
    
    # Test de creación de scrapers
    for platform in platforms:
        scraper = ScraperFactory.get_scraper(platform)
        logger.info(f"Scraper creado para {platform}: {type(scraper).__name__}")
        
        # Verificar que retorna el tipo correcto
        if platform == 'mock' and not isinstance(scraper, MockScraper):
            logger.error(f"Se esperaba MockScraper para 'mock'")
            return False
        elif platform == 'aliexpress' and not isinstance(scraper, AliExpressScraper):
            logger.error(f"Se esperaba AliExpressScraper para 'aliexpress'")
            return False
    
    # Test con plataforma inválida
    invalid_scraper = ScraperFactory.get_scraper('invalid_platform')
    if not isinstance(invalid_scraper, MockScraper):
        logger.error("Plataforma inválida debería retornar MockScraper")
        return False
    
    logger.info("✓ ScraperFactory PASSED")
    return True


def test_scrape_all_platforms():
    """
    Prueba la función scrape_all_platforms
    """
    logger.info("=== TESTING SCRAPE ALL PLATFORMS ===")
    
    products = scrape_all_platforms(count_per_platform=2)
    
    if len(products) == 0:
        logger.error("scrape_all_platforms no retornó productos")
        return False
    
    logger.info(f"scrape_all_platforms retornó {len(products)} productos totales")
    
    # Verificar que hay productos de diferentes plataformas
    platforms_found = set()
    for product in products:
        platforms_found.add(product['source_platform'])
        if not validate_product_structure(product):
            logger.error("Producto de scrape_all_platforms falló validación")
            return False
    
    logger.info(f"Plataformas encontradas en productos: {platforms_found}")
    
    expected_platforms = {'mock_aliexpress', 'aliexpress'}
    if not platforms_found.intersection(expected_platforms):
        logger.error(f"No se encontraron plataformas esperadas. Encontradas: {platforms_found}")
        return False
    
    logger.info("✓ scrape_all_platforms PASSED")
    return True


def test_data_normalization():
    """
    Prueba la normalización de datos
    """
    logger.info("=== TESTING DATA NORMALIZATION ===")
    
    scraper = MockScraper()
    
    # Test con datos de entrada variados
    test_data = [
        {
            'title': '  Test Product  ',
            'price': '25.99',
            'rating': '4.5',
            'shipping_time': '15 días',
            'url': 'https://example.com/product'
        },
        {
            'title': 'Another Product',
            'price': 35,
            'rating': 4,
            'shipping_time': 20,
        },
        {
            'title': 'Product with symbols',
            'price': '$49.99',
            'rating': '3.8 stars',
            'shipping_time': 'fast shipping',
        }
    ]
    
    for i, raw_product in enumerate(test_data):
        normalized = scraper.normalize_product(raw_product)
        logger.info(f"Producto {i+1} normalizado:")
        logger.info(f"  Título: '{normalized['title']}'")
        logger.info(f"  Precio: {normalized['price']} (tipo: {type(normalized['price'])})")
        logger.info(f"  Rating: {normalized['rating']} (tipo: {type(normalized['rating'])})")
        logger.info(f"  Envío: {normalized['shipping_time']} días")
        
        if not validate_product_structure(normalized):
            logger.error(f"Normalización del producto {i+1} falló")
            return False
    
    logger.info("✓ Data Normalization PASSED")
    return True


def run_performance_test():
    """
    Prueba de rendimiento básica
    """
    logger.info("=== PERFORMANCE TEST ===")
    
    import time
    
    # Test MockScraper
    start_time = time.time()
    mock_scraper = MockScraper()
    products = mock_scraper.scrape_products(count=10)
    mock_time = time.time() - start_time
    logger.info(f"MockScraper (10 productos): {mock_time:.3f} segundos")
    
    # Test AliExpressScraper
    start_time = time.time()
    ali_scraper = AliExpressScraper()
    products = ali_scraper.scrape_products(count=5, search_term='electronics')
    ali_time = time.time() - start_time
    logger.info(f"AliExpressScraper (5 productos): {ali_time:.3f} segundos")
    
    logger.info("✓ Performance Test COMPLETED")


def main():
    """
    Ejecuta todos los tests
    """
    logger.info("🚀 INICIANDO TESTS DEL MÓDULO SCRAPER")
    logger.info("=" * 50)
    
    tests = [
        ("MockScraper", test_mock_scraper),
        ("AliExpressScraper", test_aliexpress_scraper),
        ("ScraperFactory", test_scraper_factory),
        ("Data Normalization", test_data_normalization),
        ("Scrape All Platforms", test_scrape_all_platforms),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Ejecutando: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} EXITOSO")
            else:
                failed += 1
                logger.error(f"❌ {test_name} FALLÓ")
        except Exception as e:
            failed += 1
            logger.error(f"❌ {test_name} ERROR: {e}")
    
    # Test de rendimiento (opcional)
    try:
        run_performance_test()
    except Exception as e:
        logger.warning(f"Performance test falló: {e}")
    
    # Resumen final
    logger.info("\n" + "=" * 50)
    logger.info("📊 RESUMEN DE TESTS")
    logger.info(f"✅ Exitosos: {passed}")
    logger.info(f"❌ Fallidos: {failed}")
    logger.info(f"📈 Tasa de éxito: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        logger.info("🎉 TODOS LOS TESTS PASARON!")
    else:
        logger.warning(f"⚠️  {failed} tests fallaron")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✨ Testing completado exitosamente")
    else:
        print("\n💥 Algunos tests fallaron")
        sys.exit(1)
