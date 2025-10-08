"""
API Views para el Bot de Filtrado de AliExpress
"""

import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from products.services.bot_scraper import filter_aliexpress_products

logger = logging.getLogger('bot_api')


def filter_bot_view(request):
    """Vista principal del bot de filtrado"""
    return render(request, 'filter_bot.html')


@csrf_exempt
@require_http_methods(["POST"])
def filter_products_api(request):
    """
    API endpoint que recibe solicitudes de filtro y devuelve productos de AliExpress
    
    POST /api/filter-products/
    Body: {
        "product_name": "mouse",
        "max_price": 10.0,
        "min_rating": 4.0,
        "max_shipping": 15,
        "sort_by": "price_asc",
        "max_results": 10
    }
    """
    try:
        # Parsear datos JSON
        data = json.loads(request.body)
        
        # Extraer parámetros con valores por defecto
        product_name = data.get('product_name', '').strip()
        max_price = data.get('max_price')
        min_rating = data.get('min_rating')
        max_shipping = data.get('max_shipping')
        sort_by = data.get('sort_by', 'price_asc')
        max_results = int(data.get('max_results', 10))
        
        # Validaciones
        if not product_name:
            return JsonResponse({
                'success': False,
                'error': 'El nombre del producto es requerido'
            })
        
        if max_results > 50:
            max_results = 50
        
        # Convertir valores vacíos a None
        if max_price == '' or max_price is None:
            max_price = None
        else:
            max_price = float(max_price)
            
        if min_rating == '' or min_rating is None:
            min_rating = None
        else:
            min_rating = float(min_rating)
            
        if max_shipping == '' or max_shipping is None:
            max_shipping = None
        else:
            max_shipping = int(max_shipping)
        
        logger.info(f"🤖 Bot API: Buscando '{product_name}' con filtros")
        logger.debug(f"Filtros: precio≤{max_price}, rating≥{min_rating}, envío≤{max_shipping}")
        
        # Llamar al bot para filtrar productos
        products = filter_aliexpress_products(
            product_name=product_name,
            max_price=max_price,
            min_rating=min_rating,
            max_shipping=max_shipping,
            sort_by=sort_by,
            max_results=max_results
        )
        
        # Formatear productos para la respuesta
        formatted_products = []
        for product in products:
            formatted_products.append({
                'title': product['title'],
                'price': float(product['price']),
                'url': product['url'],
                'image': product['image'],
                'rating': float(product['rating']),
                'shipping_time': int(product['shipping_time']),
                'source_platform': product.get('source_platform', 'aliexpress')
            })
        
        logger.info(f"✅ Bot API: Devolviendo {len(formatted_products)} productos")
        
        return JsonResponse({
            'success': True,
            'products': formatted_products,
            'total_found': len(formatted_products),
            'search_term': product_name,
            'filters_applied': {
                'max_price': max_price,
                'min_rating': min_rating,
                'max_shipping': max_shipping,
                'sort_by': sort_by
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'JSON inválido en la solicitud'
        })
    
    except ValueError as e:
        return JsonResponse({
            'success': False,
            'error': f'Error en los parámetros: {str(e)}'
        })
    
    except Exception as e:
        logger.error(f"❌ Error en Bot API: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Error interno del servidor'
        })


@csrf_exempt
@require_http_methods(["GET"])
def test_bot_api(request):
    """
    Endpoint de prueba para verificar que el bot funciona
    GET /api/test-bot/?product=mouse&max_price=10
    """
    try:
        product_name = request.GET.get('product', 'mouse')
        max_price = request.GET.get('max_price')
        
        if max_price:
            max_price = float(max_price)
        
        logger.info(f"🧪 Test Bot API: '{product_name}' precio≤{max_price}")
        
        # Probar bot con parámetros básicos
        products = filter_aliexpress_products(
            product_name=product_name,
            max_price=max_price,
            max_results=5
        )
        
        return JsonResponse({
            'success': True,
            'test_result': 'Bot funcionando correctamente',
            'products_found': len(products),
            'sample_products': products[:2] if products else [],
            'timestamp': str(timezone.now()) if 'timezone' in globals() else 'N/A'
        })
        
    except Exception as e:
        logger.error(f"❌ Error en Test Bot API: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


class BotStatusView(View):
    """Vista para verificar el estado del bot"""
    
    def get(self, request):
        """GET /api/bot-status/"""
        try:
            # Hacer una búsqueda rápida para verificar que el bot funciona
            test_products = filter_aliexpress_products(
                product_name="test",
                max_results=1
            )
            
            status = {
                'bot_online': True,
                'last_test': 'successful',
                'can_search_aliexpress': len(test_products) > 0,
                'available_filters': [
                    'product_name',
                    'max_price', 
                    'min_rating',
                    'max_shipping',
                    'sort_by',
                    'max_results'
                ]
            }
            
            return JsonResponse({
                'success': True,
                'status': status
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'status': {
                    'bot_online': False,
                    'error': str(e)
                }
            })