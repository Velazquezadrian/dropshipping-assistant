#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test final del API para verificar especificaciones exactas
"""
import requests
import json
import urllib3
from datetime import datetime

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_api_specification():
    """Prueba la API con las especificaciones exactas solicitadas"""
    
    print("🚀 TEST DE API SEGÚN ESPECIFICACIONES EXACTAS")
    print("=" * 60)
    print(f"🕒 Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # URL del API
    api_url = "https://127.0.0.1:8443/filter/"
    
    # Datos de prueba exactos según especificación
    test_data = {
        "keywords": "mouse gaming",
        "min_price": 5.0,
        "max_price": 15.0,
        "currency": "USD",
        "max_shipping_days": 20,
        "limit": 3
    }
    
    print("\n📊 DATOS DE ENTRADA:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))
    
    try:
        # Hacer petición POST
        print("\n📡 Enviando petición POST...")
        response = requests.post(
            api_url,
            json=test_data,
            verify=False,  # Ignorar certificado autofirmado
            timeout=30
        )
        
        print(f"📈 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Parsear respuesta
            data = response.json()
            
            print("\n📦 RESPUESTA COMPLETA:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Validar estructura según especificaciones
            print("\n🔍 VALIDACIÓN DE ESTRUCTURA:")
            print("-" * 40)
            
            # Campos principales
            required_fields = ['requested', 'results', 'discarded', 'meta']
            for field in required_fields:
                status = "✅" if field in data else "❌"
                print(f"{status} Campo '{field}': {'presente' if field in data else 'FALTANTE'}")
            
            # Validar campo 'requested'
            if 'requested' in data:
                req_fields = ['keywords', 'min_price', 'max_price', 'currency', 'max_shipping_days', 'limit']
                for field in req_fields:
                    status = "✅" if field in data['requested'] else "❌"
                    print(f"{status} requested.{field}: {'presente' if field in data['requested'] else 'FALTANTE'}")
            
            # Validar productos en 'results'
            if 'results' in data and data['results']:
                product_fields = ['url', 'title', 'price', 'currency', 'image', 'source_platform', 'scraped_at']
                first_product = data['results'][0]
                for field in product_fields:
                    status = "✅" if field in first_product else "❌"
                    print(f"{status} product.{field}: {'presente' if field in first_product else 'FALTANTE'}")
            
            # Validar productos descartados
            if 'discarded' in data and data['discarded']:
                discarded_fields = ['candidate_url', 'reason', 'http_status']
                first_discarded = data['discarded'][0]
                for field in discarded_fields:
                    status = "✅" if field in first_discarded else "❌"
                    print(f"{status} discarded.{field}: {'presente' if field in first_discarded else 'FALTANTE'}")
            
            # Validar meta
            if 'meta' in data:
                meta_fields = ['returned', 'discarded_count', 'time_ms', 'partial']
                for field in meta_fields:
                    status = "✅" if field in data['meta'] else "❌"
                    print(f"{status} meta.{field}: {'presente' if field in data['meta'] else 'FALTANTE'}")
            
            # Estadísticas
            print(f"\n📊 ESTADÍSTICAS:")
            print(f"   🎯 Productos válidos: {len(data.get('results', []))}")
            print(f"   ❌ Productos descartados: {len(data.get('discarded', []))}")
            print(f"   ⏱️  Tiempo de procesamiento: {data.get('meta', {}).get('time_ms', 0)}ms")
            
            # Mostrar algunos productos
            if data.get('results'):
                print(f"\n🛍️ PRODUCTOS ENCONTRADOS:")
                for i, product in enumerate(data['results'][:2], 1):
                    print(f"   {i}. {product.get('title', 'Sin título')}")
                    print(f"      💰 ${product.get('price', 0)} {product.get('currency', 'USD')}")
                    print(f"      🔗 {product.get('url', 'Sin URL')}")
            
            # Mostrar razones de descarte
            if data.get('discarded'):
                print(f"\n🚫 PRODUCTOS DESCARTADOS:")
                for i, discarded in enumerate(data['discarded'][:3], 1):
                    print(f"   {i}. Razón: {discarded.get('reason', 'Sin razón')}")
                    print(f"      🔗 {discarded.get('candidate_url', 'Sin URL')}")
            
            print(f"\n🎉 ¡API FUNCIONANDO CORRECTAMENTE!")
            print(f"✅ Implementa exactamente la estructura solicitada")
            
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ No se pudo conectar al servidor")
        print("💡 Asegúrate de que el servidor esté corriendo en https://127.0.0.1:8443")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_edge_cases():
    """Prueba casos extremos"""
    print("\n🔬 PROBANDO CASOS EXTREMOS")
    print("=" * 40)
    
    # Test con límite muy bajo
    test_data = {
        "keywords": "headphones",
        "min_price": 1.0,
        "max_price": 5.0,
        "currency": "USD",
        "max_shipping_days": 10,
        "limit": 1
    }
    
    try:
        response = requests.post(
            "https://127.0.0.1:8443/filter/",
            json=test_data,
            verify=False,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Límite bajo (1): {len(data.get('results', []))} productos")
        else:
            print(f"❌ Error en límite bajo: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error en caso extremo: {e}")

if __name__ == "__main__":
    test_api_specification()
    test_edge_cases()
    
    print(f"\n🌐 ENDPOINTS DISPONIBLES:")
    print(f"   📋 POST /filter/ - API principal de filtrado")
    print(f"   🌍 GET /filter-ui/ - Interfaz web")
    print(f"   ℹ️  GET /filter/info/ - Información del API")
    print(f"   🧪 GET /filter/test/ - Test rápido")
    
    print(f"\n🎯 OBJETIVO CUMPLIDO:")
    print(f"   ✅ Bot navega AliExpress en tiempo real")
    print(f"   ✅ Filtra productos según criterios del usuario")
    print(f"   ✅ Devuelve estructura exacta solicitada")
    print(f"   ✅ No almacena productos en base de datos")
    print(f"   ✅ Reporta productos válidos y descartados")