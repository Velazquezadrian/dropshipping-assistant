#!/usr/bin/env python3
"""
Script de prueba para todos los scrapers
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
django.setup()

from products.services.scraper import ScraperFactory
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_all_scrapers():
    """Prueba todos los scrapers disponibles"""
    print("🔍 Probando todos los scrapers disponibles...")
    
    platforms = ScraperFactory.get_available_platforms()
    print(f"📋 Plataformas disponibles: {platforms}")
    
    for platform in platforms:
        print(f"\n{'='*60}")
        print(f"🛒 Probando scraper: {platform.upper()}")
        print(f"{'='*60}")
        
        try:
            scraper = ScraperFactory.get_scraper(platform)
            
            # Probar con diferentes términos según la plataforma
            if platform == 'amazon':
                search_terms = ['wireless headphones', 'smartphone case']
            elif platform == 'aliexpress':
                search_terms = ['bluetooth speaker', 'led strip']
            else:  # mock
                search_terms = ['electronics', 'gadgets']
            
            for search_term in search_terms:
                print(f"\n📱 Búsqueda: '{search_term}'")
                products = scraper.scrape_products(
                    search_term=search_term,
                    count=2
                )
                
                print(f"✅ {len(products)} productos encontrados:")
                for i, product in enumerate(products, 1):
                    print(f"  {i}. {product['title'][:45]}...")
                    print(f"     💰 ${product['price']}")
                    print(f"     ⭐ {product['rating']}/5.0")
                    print(f"     🚚 {product['shipping_time']} días")
                    print(f"     🏷️  {product['category']}")
                    print(f"     🔗 {product['url'][:50]}...")
                    print()
                
        except Exception as e:
            print(f"❌ Error probando {platform}: {e}")
    
    print(f"\n{'='*60}")
    print("🎉 Prueba de todos los scrapers completada!")
    print(f"{'='*60}")

def test_scraper_factory():
    """Prueba la funcionalidad del factory"""
    print("\n🏭 Probando ScraperFactory...")
    
    # Probar plataformas válidas
    for platform in ['mock', 'aliexpress', 'amazon']:
        scraper = ScraperFactory.get_scraper(platform)
        print(f"✅ {platform}: {scraper.__class__.__name__}")
    
    # Probar plataforma inválida
    invalid_scraper = ScraperFactory.get_scraper('invalid_platform')
    print(f"✅ invalid_platform: {invalid_scraper.__class__.__name__} (fallback)")
    
    print("✅ ScraperFactory funcionando correctamente")

if __name__ == '__main__':
    test_scraper_factory()
    test_all_scrapers()