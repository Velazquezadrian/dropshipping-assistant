"""
URL configuration for dropship_bot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import HttpResponse

@api_view(['GET'])
def health_check(request):
    """Health check simple para el root"""
    return Response({"status": "ok", "message": "Dropship Bot API está funcionando"})

def plain_health(request):
    """Health check plano sin DRF para evitar redirects"""
    return HttpResponse('ok', content_type='text/plain')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('health/', health_check, name='simple_health'),
    path('plain-health/', plain_health, name='plain_health'),
]
