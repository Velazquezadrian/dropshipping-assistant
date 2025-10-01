#!/usr/bin/env python3
"""
Script de prueba para el scraper de AliExpress
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
django.setup()

from products.services.scraper import AliExpressScraper
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_aliexpress_scraper():
    """Prueba el scraper de AliExpress"""
    print("🔍 Probando AliExpress Scraper...")
    
    # Crear instancia del scraper
    scraper = AliExpressScraper()
    
    # Términos de búsqueda para probar
    search_terms = [
        'wireless earbuds',
        'smartphone accessories',
        'led lights',
        'power bank'
    ]
    
    for search_term in search_terms:
        print(f"\n📱 Scraping: '{search_term}'")
        try:
            products = scraper.scrape_products(
                search_term=search_term,
                count=3
            )
            
            print(f"✅ {len(products)} productos encontrados:")
            for i, product in enumerate(products, 1):
                print(f"  {i}. {product['title'][:50]}...")
                print(f"     💰 ${product['price']}")
                print(f"     ⭐ {product['rating']}/5.0")
                print(f"     🚚 {product['shipping_time']} días")
                print(f"     🔗 {product['url'][:60]}...")
                print()
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("🎉 Prueba del scraper completada!")

if __name__ == '__main__':
    test_aliexpress_scraper()