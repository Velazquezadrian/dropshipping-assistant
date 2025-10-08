#!/usr/bin/env python3
"""
Test completo del scraper real de AliExpress con estrategias múltiples
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from products.services.scraper import AliExpressScraper
import logging

# Configurar logging detallado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_aliexpress_scraper_enhanced():
    """
    Prueba completa del scraper real de AliExpress con múltiples estrategias
    """
    print("="*70)
    print("🔍 PROBANDO SCRAPER REAL DE ALIEXPRESS - VERSIÓN MEJORADA")
    print("="*70)
    
    # Crear instancia del scraper
    scraper = AliExpressScraper()
    
    # Términos de búsqueda a probar con diferentes categorías
    search_tests = [
        ('electronics', 3),
        ('bluetooth earbuds', 2),
        ('phone accessories', 2),
        ('fashion', 3),
        ('home', 2)
    ]
    
    for term, count in search_tests:
        print(f"\n🔍 Buscando: '{term}' (máximo {count} productos)")
        print("-" * 50)
        
        try:
            # Realizar scraping con el método mejorado
            products = scraper.scrape_products(search_term=term, count=count)
            
            if products:
                print(f"✅ Encontrados {len(products)} productos reales:")
                
                for i, product in enumerate(products, 1):
                    print(f"\n📦 Producto {i}:")
                    print(f"   📝 Título: {product['title'][:70]}...")
                    print(f"   💰 Precio: ${product['price']}")
                    print(f"   🔗 URL: {product['url'][:90]}...")
                    print(f"   ⭐ Rating: {product.get('rating', 'N/A')}")
                    print(f"   📦 Categoría: {product.get('category', 'N/A')}")
                    print(f"   🚚 Envío: {product.get('shipping_time', 'N/A')} días")
                    
                    # Verificar que es una URL real de AliExpress
                    if 'aliexpress.com' in product['url']:
                        print(f"   ✅ URL válida de AliExpress")
                    else:
                        print(f"   ⚠️  URL no es de AliExpress")
                        
                # Estadísticas
                real_urls = sum(1 for p in products if 'aliexpress.com' in p['url'])
                print(f"\n📊 Estadísticas:")
                print(f"   - URLs reales de AliExpress: {real_urls}/{len(products)}")
                print(f"   - Precio promedio: ${sum(p['price'] for p in products)/len(products):.2f}")
                
            else:
                print("❌ No se encontraron productos")
                
        except Exception as e:
            print(f"❌ Error durante la búsqueda: {e}")
            import traceback
            print("🔍 Detalles del error:")
            traceback.print_exc()
        
        print("\n" + "="*70)

def test_search_variations():
    """Probar el sistema de variaciones de búsqueda"""
    print("\n🔍 PROBANDO SISTEMA DE VARIACIONES DE BÚSQUEDA")
    print("=" * 60)
    
    scraper = AliExpressScraper()
    
    test_terms = ['electronics', 'bluetooth', 'watch', 'phone']
    
    for term in test_terms:
        print(f"\n📝 Variaciones para '{term}':")
        try:
            variations = scraper._get_search_variations(term)
            for i, variation in enumerate(variations, 1):
                print(f"   {i}. {variation}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def test_single_product_extraction():
    """Probar extracción de un solo producto"""
    print("\n🧪 PROBANDO EXTRACCIÓN DE PRODUCTO INDIVIDUAL")
    print("=" * 60)
    
    scraper = AliExpressScraper()
    
    try:
        # Probar búsqueda de un solo término
        products = scraper._search_single_term('wireless earbuds', 1)
        
        if products:
            product = products[0]
            print(f"✅ Producto extraído exitosamente:")
            print(f"   Título: {product['title']}")
            print(f"   Precio: ${product['price']}")
            print(f"   URL: {product['url']}")
            print(f"   Datos válidos: {scraper._validate_product_data(product)}")
        else:
            print("❌ No se pudo extraer ningún producto")
            
    except Exception as e:
        print(f"❌ Error en extracción: {e}")
        import traceback
        traceback.print_exc()
                print(f"\n  {i}. {product['title'][:50]}...")
                print(f"     💰 Precio: ${product['price']}")
                print(f"     🔗 URL: {product['url']}")
                print(f"     📦 Envío: {product['shipping_time']} días")
                print(f"     ⭐ Rating: {product['rating']}")
                print(f"     🏷️ Categoría: {product['category']}")
                
                # Verificar si la URL es real
                if product['url']:
                    if 'aliexpress.com' in product['url'] and 'item' in product['url']:
                        print(f"     ✅ URL válida de AliExpress")
                    else:
                        print(f"     ⚠️  URL puede no ser válida")
                else:
                    print(f"     ❌ Sin URL")
                    
        except Exception as e:
            print(f"❌ Error buscando '{term}': {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del scraper de AliExpress...")
    
    try:
        test_aliexpress_scraper_enhanced()
        test_search_variations()
        test_single_product_extraction()
        
        print("\n✅ Todas las pruebas completadas!")
        
    except Exception as e:
        print(f"\n❌ Error general en las pruebas: {e}")
        import traceback
        traceback.print_exc()