"""
Advanced API Views para el Bot de Filtrado Avanzado
Implementa la estructura específica solicitada
"""

import json
import logging
import time
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from products.services.advanced_filter_bot import filter_aliexpress_products_advanced

logger = logging.getLogger('advanced_filter_api')


def advanced_filter_view(request):
    """Vista principal del bot de filtrado avanzado"""
    return render(request, 'advanced_filter.html')


@csrf_exempt
@require_http_methods(["POST"])
def advanced_filter_api(request):
    """
    API endpoint avanzado que implementa la estructura específica solicitada
    
    POST /filter/
    Body: {
        "keywords": "smart watch woman",
        "min_price": 10.00,
        "max_price": 60.00,
        "currency": "USD",
        "max_shipping_days": 30,
        "limit": 5
    }
    
    Response: {
        "requested": {...},
        "results": [{product}, ...],
        "discarded": [{candidate_url, reason, http_status, note?}, ...],
        "meta": {"returned": n, "discarded_count": m, "time_ms": 820, "partial": false}
    }
    """
    
    try:
        # Parsear datos JSON
        data = json.loads(request.body)
        
        # Validar campos requeridos
        keywords = data.get('keywords', '').strip()
        if not keywords:
            return JsonResponse({
                'error': 'Field "keywords" is required and cannot be empty',
                'code': 'MISSING_KEYWORDS'
            }, status=400)
        
        # Extraer parámetros con valores por defecto
        request_params = {
            'keywords': keywords,
            'min_price': float(data.get('min_price', 0.0)),
            'max_price': float(data.get('max_price', 999999.0)),
            'currency': data.get('currency', 'USD'),
            'max_shipping_days': int(data.get('max_shipping_days', 30)),
            'limit': int(data.get('limit', 5))
        }
        
        # Validaciones adicionales
        if request_params['min_price'] < 0:
            return JsonResponse({
                'error': 'min_price cannot be negative',
                'code': 'INVALID_MIN_PRICE'
            }, status=400)
        
        if request_params['max_price'] <= request_params['min_price']:
            return JsonResponse({
                'error': 'max_price must be greater than min_price',
                'code': 'INVALID_PRICE_RANGE'
            }, status=400)
        
        if request_params['limit'] <= 0 or request_params['limit'] > 50:
            return JsonResponse({
                'error': 'limit must be between 1 and 50',
                'code': 'INVALID_LIMIT'
            }, status=400)
        
        logger.info(f"🔍 Advanced Filter API: Processing '{keywords}' with filters")
        
        # Llamar al bot avanzado
        start_time = time.time()
        result = filter_aliexpress_products_advanced(request_params)
        processing_time = int((time.time() - start_time) * 1000)
        
        # Agregar tiempo de procesamiento total
        result['meta']['total_processing_time_ms'] = processing_time
        
        logger.info(f"✅ Advanced Filter API: Returned {result['meta']['returned']} products, "
                   f"{result['meta']['discarded_count']} discarded in {processing_time}ms")
        
        return JsonResponse(result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON in request body',
            'code': 'INVALID_JSON'
        }, status=400)
    
    except ValueError as e:
        return JsonResponse({
            'error': f'Invalid parameter value: {str(e)}',
            'code': 'INVALID_PARAMETER'
        }, status=400)
    
    except Exception as e:
        logger.error(f"❌ Advanced Filter API Error: {e}")
        return JsonResponse({
            'error': 'Internal server error',
            'code': 'INTERNAL_ERROR',
            'details': str(e) if logger.level == logging.DEBUG else None
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def filter_api_info(request):
    """
    Información sobre la API de filtrado avanzado
    GET /filter/info/
    """
    
    info = {
        "api_version": "1.0",
        "endpoint": "/filter/",
        "method": "POST",
        "description": "Advanced product filtering with detailed validation",
        "request_format": {
            "keywords": "string (required) - Search terms",
            "min_price": "number (optional, default: 0.0) - Minimum price filter",
            "max_price": "number (optional, default: 999999.0) - Maximum price filter", 
            "currency": "string (optional, default: 'USD') - Currency code",
            "max_shipping_days": "number (optional, default: 30) - Maximum shipping time",
            "limit": "number (optional, default: 5, max: 50) - Maximum results to return"
        },
        "response_format": {
            "requested": "object - Echo of request parameters",
            "results": "array - Valid products matching criteria",
            "discarded": "array - Rejected candidates with reasons",
            "meta": "object - Metadata about the search"
        },
        "product_fields": [
            "url", "title", "price", "currency", "image", "source_platform", "scraped_at"
        ],
        "discard_fields": [
            "candidate_url", "reason", "http_status", "note"
        ],
        "example_request": {
            "keywords": "smart watch woman",
            "min_price": 10.00,
            "max_price": 60.00,
            "currency": "USD",
            "max_shipping_days": 30,
            "limit": 5
        }
    }
    
    return JsonResponse(info)


@csrf_exempt  
@require_http_methods(["GET"])
def quick_test_filter(request):
    """
    Endpoint de prueba rápida para verificar el funcionamiento
    GET /filter/test/?keywords=mouse&limit=3
    """
    
    try:
        keywords = request.GET.get('keywords', 'test product')
        limit = int(request.GET.get('limit', 3))
        max_price = float(request.GET.get('max_price', 50.0))
        
        # Crear solicitud de prueba
        test_request = {
            'keywords': keywords,
            'min_price': 1.0,
            'max_price': max_price,
            'currency': 'USD',
            'max_shipping_days': 20,
            'limit': limit
        }
        
        logger.info(f"🧪 Quick Test: {keywords} limit={limit}")
        
        # Ejecutar filtrado
        result = filter_aliexpress_products_advanced(test_request)
        
        # Agregar información de test
        result['test_info'] = {
            'endpoint': 'quick_test_filter',
            'purpose': 'API functionality verification',
            'status': 'success'
        }
        
        return JsonResponse(result)
        
    except ValueError as e:
        return JsonResponse({
            'error': f'Invalid parameter: {str(e)}',
            'test_info': {
                'endpoint': 'quick_test_filter',
                'status': 'failed'
            }
        }, status=400)
    
    except Exception as e:
        logger.error(f"❌ Quick Test Error: {e}")
        return JsonResponse({
            'error': 'Test failed',
            'details': str(e),
            'test_info': {
                'endpoint': 'quick_test_filter', 
                'status': 'error'
            }
        }, status=500)