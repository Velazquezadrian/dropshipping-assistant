#!/usr/bin/env python
"""
Script para probar endpoints del asistente de dropshipping
"""
import requests
import json
import time

def test_endpoint(url, description):
    """Probar un endpoint y mostrar resultado"""
    print(f"\n🔍 Probando {description}...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"✅ Status Code: {response.status_code}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            data = response.json()
            print(f"📋 Response: {json.dumps(data, indent=2)}")
        else:
            print(f"📋 Response: {response.text[:200]}...")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        return False
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout de conexión")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Función principal para probar endpoints"""
    print("🚀 Probando endpoints del asistente de dropshipping")
    print("=" * 50)
    
    base_url = "http://127.0.0.1:8000"
    
    # Lista de endpoints a probar
    endpoints = [
        (f"{base_url}/health/", "Health Check"),
        (f"{base_url}/api/", "API Root"),
        (f"{base_url}/api/products/", "Products API"),
        (f"{base_url}/api/products/stats/", "Products Stats"),
        (f"{base_url}/admin/", "Admin Panel")
    ]
    
    results = []
    for url, description in endpoints:
        success = test_endpoint(url, description)
        results.append((description, success))
        time.sleep(1)  # Pausa entre requests
    
    # Resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE PRUEBAS:")
    print("=" * 50)
    
    for description, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{description:.<30} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    
    print(f"\nTotal: {passed_tests}/{total_tests} tests pasaron")
    
    if passed_tests == total_tests:
        print("🎉 ¡Todos los endpoints funcionan correctamente!")
    else:
        print("⚠️ Algunos endpoints tienen problemas")

if __name__ == "__main__":
    main()