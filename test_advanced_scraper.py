#!/usr/bin/env python3
"""
Script de prueba para el scraper avanzado de AliExpress
"""

import os
import sys
import django
from pathlib import Path
import time

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
django.setup()

from products.services.advanced_scraper import AdvancedAliExpressScraper
from products.services.scraper import ScraperFactory
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_advanced_scraper_direct():
    """Prueba directa del scraper avanzado"""
    print("🚀 Probando Scraper Avanzado Directamente...")
    
    scraper = AdvancedAliExpressScraper()
    
    search_terms = [
        'wireless earbuds',
        'led strip lights',
        'power bank',
        'bluetooth speaker'
    ]
    
    for search_term in search_terms:
        print(f"\n📱 Scraping avanzado: '{search_term}'")
        start_time = time.time()
        
        try:
            result = scraper.scrape_products_advanced(
                search_term=search_term,
                count=3,
                max_pages=2,
                concurrent_requests=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"✅ Resultado: {result.success}")
            print(f"⏱️  Tiempo: {duration:.2f} segundos")
            print(f"📦 Productos: {len(result.products)}")
            print(f"❌ Errores: {len(result.errors)}")
            print(f"📊 Metadata: {result.metadata}")
            
            if result.products:
                print("\n🏆 Productos encontrados:")
                for i, product in enumerate(result.products, 1):
                    print(f"  {i}. {product['title'][:50]}...")
                    print(f"     💰 ${product['price']}")
                    print(f"     ⭐ {product['rating']}/5.0")
                    print(f"     🚚 {product['shipping_time']} días")
                    print(f"     🏷️  {product['category']}")
                    print()
            
            if result.errors:
                print("⚠️  Errores encontrados:")
                for error in result.errors:
                    print(f"  - {error}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Prueba del scraper avanzado completada!")

def test_scraper_factory_advanced():
    """Prueba del scraper avanzado a través del factory"""
    print("\n🏭 Probando Scraper Avanzado vía Factory...")
    
    try:
        scraper = ScraperFactory.get_scraper('aliexpress_advanced')
        print(f"✅ Scraper creado: {scraper.__class__.__name__}")
        
        # Probar scraping simple
        if hasattr(scraper, 'scrape_products_advanced'):
            result = scraper.scrape_products_advanced(
                search_term='smartphone accessories',
                count=2,
                max_pages=1,
                concurrent_requests=False
            )
            
            print(f"✅ Scraping exitoso: {len(result.products)} productos")
            print(f"📊 Fallback usado: {result.metadata.get('fallback_used', False)}")
        else:
            print("⚠️  Método scrape_products_advanced no disponible")
            
    except Exception as e:
        print(f"❌ Error con factory: {e}")

def test_concurrent_vs_sequential():
    """Comparar rendimiento de scraping concurrente vs secuencial"""
    print("\n⚡ Comparando Scraping Concurrente vs Secuencial...")
    
    scraper = AdvancedAliExpressScraper()
    search_term = 'wireless charger'
    
    # Prueba secuencial
    print("\n📊 Modo Secuencial:")
    start_time = time.time()
    result_seq = scraper.scrape_products_advanced(
        search_term=search_term,
        count=4,
        max_pages=2,
        concurrent_requests=False
    )
    seq_time = time.time() - start_time
    
    print(f"  ⏱️  Tiempo: {seq_time:.2f}s")
    print(f"  📦 Productos: {len(result_seq.products)}")
    
    # Esperar un momento entre pruebas
    time.sleep(2)
    
    # Prueba concurrente
    print("\n🚀 Modo Concurrente:")
    start_time = time.time()
    result_conc = scraper.scrape_products_advanced(
        search_term=search_term,
        count=4,
        max_pages=2,
        concurrent_requests=True
    )
    conc_time = time.time() - start_time
    
    print(f"  ⏱️  Tiempo: {conc_time:.2f}s")
    print(f"  📦 Productos: {len(result_conc.products)}")
    
    # Comparación
    if seq_time > 0:
        speedup = seq_time / conc_time if conc_time > 0 else 0
        print(f"\n📈 Speedup: {speedup:.2f}x más rápido")

def test_advanced_features():
    """Probar características avanzadas del scraper"""
    print("\n🔧 Probando Características Avanzadas...")
    
    scraper = AdvancedAliExpressScraper()
    
    # Probar optimización de términos
    test_terms = [
        'phone', 'smartphone', 'mobile device',
        'led', 'lights', 'lighting',
        'car mount', 'automotive', 'vehicle'
    ]
    
    print("\n🎯 Optimización de Términos de Búsqueda:")
    for term in test_terms:
        optimized = scraper._optimize_search_term_advanced(term)
        print(f"  '{term}' -> '{optimized}'")
    
    # Probar categorización avanzada
    print("\n🏷️  Categorización Avanzada:")
    test_products = [
        "Wireless Bluetooth 5.0 Earbuds with Charging Case",
        "Smart LED Strip Lights RGB Color Changing",
        "Magnetic Car Phone Mount Dashboard Holder",
        "Stainless Steel Jewelry Necklace Pendant",
        "Fitness Tracker Smart Watch Heart Rate Monitor"
    ]
    
    for product_title in test_products:
        category = scraper._determine_category_advanced("", product_title)
        print(f"  '{product_title[:40]}...' -> {category}")

if __name__ == '__main__':
    print("🧪 TESTING SCRAPER AVANZADO DE ALIEXPRESS")
    print("=" * 60)
    
    # Ejecutar todas las pruebas
    test_advanced_scraper_direct()
    test_scraper_factory_advanced()
    test_concurrent_vs_sequential()
    test_advanced_features()
    
    print("\n" + "=" * 60)
    print("🎊 TODAS LAS PRUEBAS COMPLETADAS")
    print("=" * 60)