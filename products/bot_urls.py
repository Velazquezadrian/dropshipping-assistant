"""
URLs para el Bot de Filtrado de AliExpress
"""

from django.urls import path
from products.bot_views import (
    filter_bot_view,
    filter_products_api,
    test_bot_api,
    BotStatusView
)

bot_urlpatterns = [
    # Página principal del bot
    path('filter/', filter_bot_view, name='filter_bot'),
    
    # API endpoints
    path('api/filter-products/', filter_products_api, name='filter_products_api'),
    path('api/test-bot/', test_bot_api, name='test_bot_api'),
    path('api/bot-status/', BotStatusView.as_view(), name='bot_status'),
]

# Asignar a urlpatterns para Django
urlpatterns = bot_urlpatterns