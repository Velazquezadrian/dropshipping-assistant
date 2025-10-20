#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Views simplificadas para el bot de informática
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import logging
from .services.informatica_bot import InformaticaBot

logger = logging.getLogger('informatica_views')

@csrf_exempt
def buscar_informatica(request):
    """
    Endpoint simplificado para buscar productos de informática
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            categoria = data.get('categoria')  # Opcional
            limite = data.get('limite', 10)
            
        except json.JSONDecodeError:
            # Si no hay JSON, usar defaults
            categoria = None
            limite = 10
    else:
        # GET request - usar parámetros de URL
        categoria = request.GET.get('categoria')
        limite = int(request.GET.get('limite', 10))
    
    try:
        # Crear bot y buscar productos
        bot = InformaticaBot()
        productos = bot.buscar_productos_informatica(categoria, limite)
        
        # Formatear respuesta
        respuesta = {
            'exito': True,
            'categoria_buscada': categoria or 'todas',
            'productos_encontrados': len(productos),
            'productos': productos,
            'categorias_disponibles': list(bot.categorias_informatica.keys())
        }
        
        logger.info(f"✅ Búsqueda exitosa: {len(productos)} productos de informática")
        return JsonResponse(respuesta)
        
    except Exception as e:
        logger.error(f"❌ Error en búsqueda: {e}")
        return JsonResponse({
            'exito': False,
            'error': str(e),
            'mensaje': 'Error buscando productos de informática'
        }, status=500)

@csrf_exempt  
def categorias_informatica(request):
    """
    Endpoint para obtener todas las categorías disponibles
    """
    try:
        bot = InformaticaBot()
        
        respuesta = {
            'exito': True,
            'categorias': bot.categorias_informatica,
            'total_categorias': len(bot.categorias_informatica)
        }
        
        return JsonResponse(respuesta)
        
    except Exception as e:
        logger.error(f"❌ Error obteniendo categorías: {e}")
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
def resumen_productos(request):
    """
    Endpoint para obtener resumen de productos por categoría
    """
    try:
        bot = InformaticaBot()
        resumen = bot.obtener_resumen_categorias()
        
        respuesta = {
            'exito': True,
            'resumen_por_categoria': resumen,
            'total_productos': sum(resumen.values())
        }
        
        return JsonResponse(respuesta)
        
    except Exception as e:
        logger.error(f"❌ Error en resumen: {e}")
        return JsonResponse({
            'exito': False,
            'error': str(e)
        }, status=500)