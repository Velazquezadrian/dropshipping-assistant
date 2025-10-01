#!/usr/bin/env python
"""
Prueba directa del sistema de notificaciones avanzado
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dropship_bot.settings')
django.setup()

from products.models import Product
from products.services.notifications import notification_manager

def test_notification_system():
    """Probar el sistema de notificaciones"""
    print("🧪 PRUEBA DEL SISTEMA DE NOTIFICACIONES AVANZADO")
    print("=" * 60)
    
    # Obtener un producto de prueba
    try:
        product = Product.objects.get(id=64)  # Cable USB-C para ofertas especiales
        print(f"📦 Producto: {product.title}")
        print(f"💰 Precio: ${product.price}")
        print(f"⭐ Rating: {product.rating}")
        print(f"🔗 Plataforma: {product.source_platform}")
        print()
        
        # Probar notificación
        results = notification_manager.notify_new_product(product)
        
        print("📨 RESULTADOS:")
        for platform, result in results.items():
            status = "✅ Enviado" if result['sent'] else "❌ Error" if result.get('error') else "🔒 Filtrado"
            print(f"   {platform}: {status}")
            
            if result.get('rules_matched'):
                print(f"      📋 Reglas: {', '.join(result['rules_matched'])}")
            if result.get('template_used'):
                print(f"      🎨 Plantilla: {result['template_used']}")
            if result.get('error'):
                print(f"      ❌ Error: {result['error']}")
            print()
        
        # Mostrar estadísticas
        print("📊 ESTADÍSTICAS ACTUALIZADAS:")
        stats = notification_manager.get_system_stats()
        for service_name, service_stats in stats['services'].items():
            print(f"   {service_name}: {service_stats['sent']} enviadas | {service_stats['failed']} fallidas | {service_stats['filtered']} filtradas")
        
    except Product.DoesNotExist:
        print("❌ Producto con ID 61 no encontrado")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_notification_system()