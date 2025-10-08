#!/usr/bin/env python3
"""
🔍 VERIFICACIÓN COMPLETA: ¿EL BOT DA LINKS REALES?
Prueba exhaustiva del bot para confirmar que devuelve productos reales de internet
"""

import os
import sys
import django
import requests
import time
from datetime import datetime

# Configurar Django
sys.path.append(r'C:\Dropshiping')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
django.setup()

from products.services.bot_scraper import filter_aliexpress_products

def verificar_url_es_real(url, timeout=10):
    """Verifica si una URL es accesible y contiene un producto real"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        print(f"  🔍 Verificando: {url}")
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
        
        # Verificar que no sea página de error
        if response.status_code == 200:
            content = response.text.lower()
            
            # Verificar que NO sea página de error 404
            if 'error/404' in response.url or '404' in content[:1000]:
                return False, "Redirige a página 404"
            
            # Verificar que contenga elementos típicos de producto
            product_indicators = [
                'price', 'buy', 'cart', 'product', 'item', 
                'aliexpress', 'seller', 'shipping', 'review'
            ]
            
            found_indicators = sum(1 for indicator in product_indicators if indicator in content)
            
            if found_indicators >= 3:
                return True, f"Página válida con {found_indicators} indicadores de producto"
            else:
                return False, f"Solo {found_indicators} indicadores encontrados"
        else:
            return False, f"HTTP {response.status_code}"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_bot_productos_reales():
    """Prueba si el bot devuelve productos con URLs reales"""
    print("🤖 PROBANDO BOT CON VERIFICACIÓN DE URLs REALES")
    print("=" * 60)
    
    # Test 1: Mouse baratos
    print("\n📝 Test 1: 'Busca mouse que cuesten menos de $15'")
    productos = filter_aliexpress_products(
        product_name="mouse",
        max_price=15.0,
        max_results=5
    )
    
    print(f"✅ Bot encontró: {len(productos)} productos")
    
    urls_validas = 0
    urls_invalidas = 0
    
    for i, producto in enumerate(productos, 1):
        print(f"\n  {i}. {producto['title'][:50]}...")
        print(f"     💰 ${producto['price']} | ⭐ {producto['rating']} | 🚚 {producto['shipping_time']} días")
        
        # Verificar si el URL es real
        es_real, motivo = verificar_url_es_real(producto['url'])
        
        if es_real:
            print(f"     ✅ URL REAL: {producto['url']}")
            print(f"     ✅ {motivo}")
            urls_validas += 1
        else:
            print(f"     ❌ URL INVÁLIDA: {producto['url']}")
            print(f"     ❌ {motivo}")
            urls_invalidas += 1
        
        time.sleep(1)  # Pausa para no sobrecargar
    
    print(f"\n📊 RESULTADO TEST 1:")
    print(f"✅ URLs válidas: {urls_validas}")
    print(f"❌ URLs inválidas: {urls_invalidas}")
    print(f"📈 Tasa de éxito: {(urls_validas / len(productos) * 100):.1f}%")
    
    return urls_validas, urls_invalidas

def test_diferentes_productos():
    """Prueba con diferentes tipos de productos"""
    print(f"\n🔄 PROBANDO DIFERENTES PRODUCTOS")
    print("=" * 50)
    
    productos_test = [
        {"name": "keyboard", "max_price": 20, "descripcion": "Teclados baratos"},
        {"name": "headphones", "max_price": 25, "descripcion": "Auriculares económicos"},
        {"name": "cable usb", "max_price": 5, "descripcion": "Cables USB baratos"}
    ]
    
    total_validas = 0
    total_invalidas = 0
    
    for test in productos_test:
        print(f"\n📂 Probando: {test['descripcion']}")
        
        productos = filter_aliexpress_products(
            product_name=test["name"],
            max_price=test["max_price"],
            max_results=3
        )
        
        print(f"   📦 Encontrados: {len(productos)} productos")
        
        for i, producto in enumerate(productos, 1):
            print(f"   {i}. {producto['title'][:40]}... - ${producto['price']}")
            
            # Verificación rápida de URL
            es_real, _ = verificar_url_es_real(producto['url'], timeout=5)
            
            if es_real:
                print(f"      ✅ URL real")
                total_validas += 1
            else:
                print(f"      ❌ URL inválida")
                total_invalidas += 1
    
    print(f"\n📊 RESULTADO GENERAL:")
    print(f"✅ Total URLs válidas: {total_validas}")
    print(f"❌ Total URLs inválidas: {total_invalidas}")
    
    return total_validas, total_invalidas

def test_scraping_real_aliexpress():
    """Intenta hacer scraping real de AliExpress"""
    print(f"\n🌐 PROBANDO SCRAPING REAL DE ALIEXPRESS")
    print("=" * 50)
    
    from products.services.bot_scraper import AliExpressBot
    
    bot = AliExpressBot()
    
    # Intentar búsqueda real
    print("🔍 Intentando búsqueda real en AliExpress...")
    
    try:
        # Usar el método interno de búsqueda
        productos_raw = bot._search_aliexpress("mouse", 5)
        
        print(f"📦 Scraping devolvió: {len(productos_raw)} productos")
        
        if productos_raw:
            print("✅ ¡El bot SÍ puede extraer productos!")
            
            for i, producto in enumerate(productos_raw[:3], 1):
                print(f"  {i}. {producto['title'][:50]}...")
                print(f"     💰 ${producto['price']} | 🔗 {producto['url']}")
                
                # Verificar URL
                es_real, motivo = verificar_url_es_real(producto['url'], timeout=5)
                print(f"     {'✅' if es_real else '❌'} {motivo}")
        else:
            print("⚠️  Scraping real falló, usando productos simulados")
            
    except Exception as e:
        print(f"❌ Error en scraping real: {e}")

def main():
    print("🚀 VERIFICACIÓN EXHAUSTIVA DEL BOT")
    print("=" * 70)
    print(f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Objetivo: Verificar que el bot devuelve URLs REALES de productos")
    
    # Test 1: Productos principales
    validas1, invalidas1 = test_bot_productos_reales()
    
    # Test 2: Diferentes productos
    validas2, invalidas2 = test_diferentes_productos()
    
    # Test 3: Scraping real
    test_scraping_real_aliexpress()
    
    # Resultado final
    total_validas = validas1 + validas2
    total_invalidas = invalidas1 + invalidas2
    total_productos = total_validas + total_invalidas
    
    print(f"\n🏆 CONCLUSIÓN FINAL:")
    print(f"📦 Total productos probados: {total_productos}")
    print(f"✅ URLs válidas: {total_validas}")
    print(f"❌ URLs inválidas: {total_invalidas}")
    
    if total_productos > 0:
        tasa_exito = (total_validas / total_productos) * 100
        print(f"📈 Tasa de éxito: {tasa_exito:.1f}%")
        
        if tasa_exito >= 80:
            print("🎉 ¡EXCELENTE! El bot devuelve URLs reales de productos")
        elif tasa_exito >= 50:
            print("✅ BUENO: La mayoría de URLs son válidas")
        else:
            print("⚠️  NECESITA MEJORAS: Muchas URLs no son válidas")
    
    print(f"\n🌐 Para probar manualmente:")
    print(f"1. Ir a: http://localhost:8000/filter/")
    print(f"2. Buscar: 'mouse', precio máximo: '10'")
    print(f"3. Verificar que los links funcionen en el navegador")

if __name__ == "__main__":
    main()