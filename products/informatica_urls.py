#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
URLs para el bot de informática simplificado
"""

from django.urls import path
from . import informatica_views

urlpatterns = [
    # Endpoint principal - buscar productos de informática
    path('informatica/', informatica_views.buscar_informatica, name='buscar_informatica'),
    
    # Obtener categorías disponibles
    path('informatica/categorias/', informatica_views.categorias_informatica, name='categorias_informatica'),
    
    # Resumen de productos por categoría
    path('informatica/resumen/', informatica_views.resumen_productos, name='resumen_productos'),
]