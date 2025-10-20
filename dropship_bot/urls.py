"""
URL configuration for dropship_bot project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse
from products.home_views import home_view, execute_bot_view

@api_view(['GET'])
def health_check(request):
    """Health check simple para el root"""
    return Response({"status": "ok", "message": "Dropship Bot API está funcionando"})

def plain_health(request):
    """Health check plano sin DRF para evitar redirects"""
    return HttpResponse('ok', content_type='text/plain')

urlpatterns = [
    # Página principal
    path('', home_view, name='home'),
    path('api/execute-bot/', execute_bot_view, name='execute-bot'),
    
    path('admin/', admin.site.urls),
    
    # URLs de productos principales
    path('', include('products.urls')),
    
    path('health/', health_check, name='simple_health'),
    path('plain-health/', plain_health, name='plain_health'),
]
