#!/usr/bin/env python
"""
Script de monitoreo del sistema de dropshipping
Verifica el estado del servidor y la base de datos
"""
import os
import sys
import django
import requests
import time
from datetime import datetime

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
django.setup()

from products.models import Product

def check_server_health():
    """Verificar que el servidor responda"""
    try:
        response = requests.get('http://127.0.0.1:8001/health/', timeout=5)
        if response.status_code == 200:
            print("✅ Servidor: OK")
            return True
        else:
            print(f"❌ Servidor: Error {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Servidor: No responde - {e}")
        return False

def check_database():
    """Verificar el estado de la base de datos"""
    try:
        total_products = Product.objects.count()
        recent_products = Product.objects.filter(created_at__gte=datetime.now().date()).count()
        print(f"✅ Base de datos: OK ({total_products} productos, {recent_products} hoy)")
        return True
    except Exception as e:
        print(f"❌ Base de datos: Error - {e}")
        return False

def check_api_endpoints():
    """Verificar endpoints principales de la API"""
    endpoints = [
        '/api/products/',
        '/api/products/stats/',
    ]
    
    all_ok = True
    for endpoint in endpoints:
        try:
            response = requests.get(f'http://127.0.0.1:8001{endpoint}', timeout=5)
            if response.status_code == 200:
                print(f"✅ API {endpoint}: OK")
            else:
                print(f"❌ API {endpoint}: Error {response.status_code}")
                all_ok = False
        except requests.exceptions.RequestException as e:
            print(f"❌ API {endpoint}: No responde - {e}")
            all_ok = False
    
    return all_ok

def main():
    """Función principal de monitoreo"""
    print("🔍 === MONITOREO DEL SISTEMA DE DROPSHIPPING ===")
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    # Verificar componentes
    server_ok = check_server_health()
    db_ok = check_database()
    api_ok = check_api_endpoints()
    
    print("=" * 50)
    
    # Resumen
    if all([server_ok, db_ok, api_ok]):
        print("🎉 Sistema: FUNCIONANDO CORRECTAMENTE")
        return 0
    else:
        print("⚠️ Sistema: HAY PROBLEMAS")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)