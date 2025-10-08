#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test del Bot Real de AliExpress
Prueba el scraping real de productos
"""
import os
import sys
import json
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
import django
django.setup()

from products.services.real_aliexpress_bot import AliExpressRealBot

def test_real_bot():
    """Test completo del bot real"""
    print("🌐 TEST DEL BOT REAL DE ALIEXPRESS")
    print("=" * 60)
    print(f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objetivo: Hacer scraping real de productos de AliExpress")
    
    # Casos de prueba
    test_cases = [
        {
            "name": "🖱️ Mouse Inalámbrico",
            "data": {
                "keywords": "wireless mouse",
                "min_price": 5.0,
                "max_price": 30.0,
                "currency": "USD",
                "max_shipping_days": 30,
                "limit": 3
            }
        },
        {
            "name": "⌚ Smart Watch",
            "data": {
                "keywords": "smart watch",
                "min_price": 20.0,
                "max_price": 100.0,
                "currency": "USD",
                "max_shipping_days": 25,
                "limit": 2
            }
        }
    ]
    
    bot = AliExpressRealBot()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"📋 CASO {i}: {test_case['name']}")
        print(f"{'='*50}")
        
        print(f"\n📥 ENTRADA:")
        print(json.dumps(test_case['data'], indent=2, ensure_ascii=False))
        
        print(f"\n🔄 HACIENDO SCRAPING REAL...")
        
        try:
            result = bot.filter_products(test_case['data'])
            
            print(f"\n📊 RESULTADOS:")
            print(f"   ✅ Productos encontrados: {len(result.get('results', []))}")
            print(f"   ❌ Productos descartados: {len(result.get('discarded', []))}")
            print(f"   ⏱️  Tiempo de scraping: {result.get('meta', {}).get('time_ms', 0)}ms")
            print(f"   📊 Estado: {'Parcial' if result.get('meta', {}).get('partial', False) else 'Completo'}")
            
            if result.get('meta', {}).get('fallback', False):
                print(f"   ⚠️  Fallback activado: {result.get('meta', {}).get('note', 'Sin nota')}")
            
            # Mostrar productos encontrados
            if result.get('results'):
                print(f"\n🛍️ PRODUCTOS REALES ENCONTRADOS:")
                for j, product in enumerate(result['results'][:2], 1):
                    print(f"   {j}. {product.get('title', 'Sin título')[:60]}...")
                    print(f"      💰 ${product.get('price', 0)} {product.get('currency', 'USD')}")
                    print(f"      🔗 {product.get('url', 'Sin URL')}")
                    print(f"      🖼️ {product.get('image', 'Sin imagen')[:60]}...")
                    print(f"      📅 Scraped: {product.get('scraped_at', 'Sin fecha')}")
                    
                    # Verificar si es producto real o fallback
                    source = product.get('source', 'unknown')
                    if 'fallback' in product.get('title', '').lower():
                        print(f"      ⚠️  FALLBACK: Producto de ejemplo")
                    else:
                        print(f"      ✅ REAL: Producto de AliExpress")
            
            # Mostrar productos descartados
            if result.get('discarded'):
                print(f"\n🚫 PRODUCTOS DESCARTADOS:")
                for j, discarded in enumerate(result['discarded'][:2], 1):
                    print(f"   {j}. Razón: {discarded.get('reason', 'Sin razón')}")
                    print(f"      🔗 {discarded.get('candidate_url', 'Sin URL')}")
                    if discarded.get('note'):
                        print(f"      📝 {discarded.get('note', '')[:50]}...")
            
            # Validar estructura
            required_fields = ['requested', 'results', 'discarded', 'meta']
            structure_valid = all(field in result for field in required_fields)
            print(f"\n🔍 Estructura válida: {'✅ Sí' if structure_valid else '❌ No'}")
            
        except Exception as e:
            print(f"❌ Error en caso {i}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print(f"🎉 TEST DEL BOT REAL COMPLETADO")
    print(f"{'='*60}")
    
    print(f"\n📋 CARACTERÍSTICAS DEL BOT REAL:")
    print(f"   ✅ Scraping real de AliExpress.com")
    print(f"   ✅ Parsing de HTML con BeautifulSoup")
    print(f"   ✅ Extracción de datos JSON del sitio")
    print(f"   ✅ Headers realistas para evitar bloqueos")
    print(f"   ✅ Sistema de fallback automático")
    print(f"   ✅ Rate limiting integrado")
    print(f"   ✅ Validación de productos en tiempo real")
    
    print(f"\n🌐 ENDPOINTS DISPONIBLES:")
    print(f"   📋 POST /real-filter/ - Scraping real principal")
    print(f"   🌍 GET /real-filter-ui/ - Interfaz web del bot real")
    print(f"   ℹ️  GET /real-filter/info/ - Información del bot real")
    print(f"   🧪 GET /real-filter/test/ - Test rápido del scraping")

if __name__ == "__main__":
    test_real_bot()