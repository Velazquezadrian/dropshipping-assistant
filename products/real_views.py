#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vistas para el Bot Real de AliExpress
API endpoints que usan scraping real
"""

import json
import logging
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from products.services.real_aliexpress_bot import AliExpressRealBot

logger = logging.getLogger('real_bot_views')

@csrf_exempt
@require_http_methods(["POST"])
def real_filter_api(request):
    """
    API principal para filtrado con scraping real de AliExpress
    
    POST /real-filter/
    """
    try:
        # Parsear datos JSON del cuerpo de la petición
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            return JsonResponse({
                'error': 'Content-Type must be application/json',
                'expected_format': {
                    'keywords': 'string',
                    'min_price': 'float',
                    'max_price': 'float',
                    'currency': 'string (USD, EUR)',
                    'max_shipping_days': 'integer',
                    'limit': 'integer (1-20)'
                }
            }, status=400)
        
        # Validar campos requeridos
        required_fields = ['keywords', 'min_price', 'max_price', 'currency', 'max_shipping_days', 'limit']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            return JsonResponse({
                'error': f'Missing required fields: {", ".join(missing_fields)}',
                'received': list(data.keys()),
                'required': required_fields
            }, status=400)
        
        # Validar tipos y rangos
        try:
            keywords = str(data['keywords']).strip()
            min_price = float(data['min_price'])
            max_price = float(data['max_price'])
            currency = str(data['currency']).upper()
            max_shipping_days = int(data['max_shipping_days'])
            limit = int(data['limit'])
            
            if not keywords:
                return JsonResponse({'error': 'Keywords cannot be empty'}, status=400)
            
            if min_price < 0 or max_price < 0:
                return JsonResponse({'error': 'Prices cannot be negative'}, status=400)
            
            if min_price >= max_price:
                return JsonResponse({'error': 'min_price must be less than max_price'}, status=400)
            
            if currency not in ['USD', 'EUR']:
                return JsonResponse({'error': 'Currency must be USD or EUR'}, status=400)
            
            if limit < 1 or limit > 20:
                return JsonResponse({'error': 'Limit must be between 1 and 20'}, status=400)
            
            if max_shipping_days < 1 or max_shipping_days > 60:
                return JsonResponse({'error': 'max_shipping_days must be between 1 and 60'}, status=400)
                
        except (ValueError, TypeError) as e:
            return JsonResponse({'error': f'Invalid data types: {str(e)}'}, status=400)
        
        # Procesar con el bot real
        logger.info(f"🤖 Real Bot: Procesando '{keywords}' ${min_price}-${max_price}")
        
        bot = AliExpressRealBot()
        result = bot.filter_products(data)
        
        # Agregar headers de respuesta
        response = JsonResponse(result, json_dumps_params={'indent': 2, 'ensure_ascii': False})
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type'
        
        logger.info(f"✅ Real Bot: Devuelto {result['meta']['returned']} productos reales")
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body'}, status=400)
    except Exception as e:
        logger.error(f"❌ Error en real filter API: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e),
            'type': 'real_bot_error'
        }, status=500)

@require_http_methods(["GET"])
def real_filter_info(request):
    """
    Información sobre el API de filtrado real
    
    GET /real-filter/info/
    """
    info = {
        "name": "Real AliExpress Filter API",
        "version": "2.0",
        "description": "Bot que hace scraping real de AliExpress y filtra productos",
        "features": [
            "Scraping real de productos de AliExpress",
            "Filtrado por precio, envío y keywords",
            "Validación de productos en tiempo real",
            "Análisis detallado de productos descartados",
            "Fallback automático en caso de errores"
        ],
        "endpoints": {
            "POST /real-filter/": "Filtrado principal con scraping real",
            "GET /real-filter/info/": "Información del API",
            "GET /real-filter/test/": "Test rápido del sistema",
            "GET /real-filter-ui/": "Interfaz web para filtrado real"
        },
        "input_format": {
            "keywords": "string - Términos de búsqueda",
            "min_price": "float - Precio mínimo en USD/EUR",
            "max_price": "float - Precio máximo en USD/EUR", 
            "currency": "string - USD o EUR",
            "max_shipping_days": "integer - Máximo días de envío (1-60)",
            "limit": "integer - Límite de productos (1-20)"
        },
        "output_format": {
            "requested": "object - Parámetros de entrada",
            "results": "array - Productos válidos encontrados",
            "discarded": "array - Productos descartados con razones",
            "meta": "object - Metadatos (tiempo, contadores, etc.)"
        },
        "status": "active",
        "real_scraping": True,
        "rate_limiting": "1-3 segundos entre peticiones",
        "data_source": "AliExpress.com (scraping real)"
    }
    
    response = JsonResponse(info, json_dumps_params={'indent': 2})
    response['Access-Control-Allow-Origin'] = '*'
    return response

@require_http_methods(["GET"])
def real_quick_test(request):
    """
    Test rápido del sistema de scraping real
    
    GET /real-filter/test/
    """
    try:
        logger.info("🧪 Ejecutando test rápido del bot real")
        
        # Datos de test
        test_data = {
            "keywords": "wireless mouse",
            "min_price": 5.0,
            "max_price": 30.0,
            "currency": "USD",
            "max_shipping_days": 25,
            "limit": 3
        }
        
        # Ejecutar bot real
        bot = AliExpressRealBot()
        result = bot.filter_products(test_data)
        
        # Agregar información de test
        result['test_info'] = {
            'type': 'quick_test',
            'description': 'Test automático del sistema de scraping real',
            'test_data': test_data,
            'timestamp': result.get('meta', {}).get('scraped_at', 'unknown')
        }
        
        response = JsonResponse(result, json_dumps_params={'indent': 2})
        response['Access-Control-Allow-Origin'] = '*'
        
        logger.info(f"✅ Test completado: {result['meta']['returned']} productos")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error en test rápido: {e}")
        return JsonResponse({
            'error': 'Test failed',
            'message': str(e),
            'test_status': 'failed'
        }, status=500)

def real_filter_view(request):
    """
    Interfaz web para el filtrado real de AliExpress
    
    GET /real-filter-ui/
    """
    return render(request, 'real_filter.html', {
        'title': 'Real AliExpress Filter',
        'api_endpoint': '/real-filter/',
        'description': 'Busca productos reales de AliExpress con scraping en tiempo real'
    })

@csrf_exempt
@require_http_methods(["OPTIONS"])
def real_filter_options(request):
    """Manejar peticiones OPTIONS para CORS"""
    response = HttpResponse()
    response['Access-Control-Allow-Origin'] = '*'
    response['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response