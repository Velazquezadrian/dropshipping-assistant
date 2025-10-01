"""
URLs para la aplicación de productos
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, HealthCheckViewSet

# Router de DRF
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'health', HealthCheckViewSet, basename='health')

urlpatterns = [
    path('api/', include(router.urls)),
]