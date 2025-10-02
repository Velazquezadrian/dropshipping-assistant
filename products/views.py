"""
Vistas para la API REST de productos
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Min, Max, Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from celery.result import AsyncResult
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, ScrapeJob
from .serializers import (
    ProductSerializer,
    ProductCreateSerializer,
    ProductListSerializer,
    ProductStatsSerializer,
    HealthCheckSerializer,
    ScrapeJobSerializer,
)
from .services.filters import create_filter_from_params

logger = logging.getLogger('products')


class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de productos
    """
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'category']
    ordering_fields = ['created_at', 'price', 'rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción"""
        if self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'list':
            return ProductListSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """
        Aplica filtros personalizados al queryset
        """
        queryset = super().get_queryset()
        
        # Aplicar filtros personalizados
        filter_params = {
            'min_price': self.request.query_params.get('min_price'),
            'max_price': self.request.query_params.get('max_price'),
            'keywords': self.request.query_params.get('keywords'),
            'max_shipping_days': self.request.query_params.get('max_shipping_days'),
            'min_rating': self.request.query_params.get('min_rating'),
            'platforms': self.request.query_params.get('platforms'),
            'categories': self.request.query_params.get('categories'),
        }
        
        # Remover parámetros vacíos
        filter_params = {k: v for k, v in filter_params.items() if v is not None and v != ''}
        
        if filter_params:
            product_filter = create_filter_from_params(**filter_params)
            queryset = product_filter.filter_queryset(queryset)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Endpoint para obtener estadísticas de productos
        """
        try:
            queryset = self.get_queryset()
            
            # Estadísticas básicas
            stats = queryset.aggregate(
                total_products=Count('id'),
                average_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price')
            )
            
            # Plataformas y categorías únicas
            platforms = list(queryset.values_list('source_platform', flat=True).distinct())
            categories = list(queryset.values_list('category', flat=True).distinct())
            categories = [cat for cat in categories if cat]  # Remover valores vacíos
            
            # Productos agregados hoy y esta semana
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            
            stats['platforms'] = platforms
            stats['categories'] = categories
            stats['products_today'] = queryset.filter(created_at__date=today).count()
            stats['products_this_week'] = queryset.filter(created_at__date__gte=week_ago).count()
            
            # Manejar valores None
            stats['average_price'] = stats['average_price'] or 0
            stats['min_price'] = stats['min_price'] or 0
            stats['max_price'] = stats['max_price'] or 0
            stats['total_products'] = stats['total_products'] or 0
            
            serializer = ProductStatsSerializer(stats)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Endpoint para obtener productos agregados recientemente
        """
        try:
            # Productos de las últimas 24 horas
            yesterday = timezone.now() - timedelta(hours=24)
            recent_products = self.get_queryset().filter(created_at__gte=yesterday)
            
            # Paginación
            page = self.paginate_queryset(recent_products)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(recent_products, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo productos recientes: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def by_platform(self, request):
        """
        Endpoint para obtener productos agrupados por plataforma
        """
        try:
            platform = request.query_params.get('platform')
            if not platform:
                return Response(
                    {'error': 'Parámetro platform requerido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            products = self.get_queryset().filter(source_platform__iexact=platform)
            
            # Paginación
            page = self.paginate_queryset(products)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = self.get_serializer(products, many=True)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error obteniendo productos por plataforma: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class HealthCheckViewSet(viewsets.ViewSet):
    """
    ViewSet para health check del sistema
    """
    
    @action(detail=False, methods=['get'])
    def status(self, request):
        """
        Endpoint de health check
        """
        try:
            # Verificar conexión a base de datos
            db_status = "ok"
            products_count = 0
            last_scrape = None
            
            try:
                products_count = Product.objects.count()
                # Obtener el producto más reciente para determinar último scrape
                latest_product = Product.objects.order_by('-created_at').first()
                if latest_product:
                    last_scrape = latest_product.created_at
            except Exception as e:
                db_status = f"error: {str(e)}"
                logger.error(f"Error en health check de DB: {e}")
            
            health_data = {
                'status': 'ok' if db_status == 'ok' else 'error',
                'timestamp': timezone.now(),
                'database': db_status,
                'products_count': products_count,
                'last_scrape': last_scrape
            }
            
            serializer = HealthCheckSerializer(health_data)
            
            response_status = status.HTTP_200_OK if health_data['status'] == 'ok' else status.HTTP_503_SERVICE_UNAVAILABLE
            return Response(serializer.data, status=response_status)
            
        except Exception as e:
            logger.error(f"Error en health check: {e}")
            return Response(
                {
                    'status': 'error',
                    'timestamp': timezone.now(),
                    'error': str(e)
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )


class AsyncScrapeLaunchView(APIView):
    """Lanza tarea Celery de scraping asincrónico."""
    def post(self, request):
        payload = request.data or {}
        query = payload.get('query')
        if not query:
            return Response({'error': 'query es requerido'}, status=400)
        source = payload.get('source', 'aliexpress_advanced')
        max_pages = int(payload.get('max_pages', 1))
        # Crear ScrapeJob
        job = ScrapeJob.objects.create(
            query=query,
            source=source,
            requested_pages=max_pages,
        )
        from .tasks import scrape_products_async  # import diferido
        task = scrape_products_async.delay(query=query, source=source, max_pages=max_pages, job_id=str(job.id))
        job.task_id = task.id
        job.save(update_fields=['task_id'])
        return Response({'task_id': task.id, 'job_id': str(job.id), 'status': 'submitted'})


class AsyncScrapeStatusView(APIView):
    """Retorna estado y resultado (si listo) de una tarea Celery."""
    def get(self, request, task_id: str):
        result = AsyncResult(task_id)
        data = {
            'task_id': task_id,
            'state': result.state,
        }
        if result.successful():
            data['result'] = result.result
        elif result.failed():
            data['error'] = str(result.result)
        return Response(data)


class ScrapeJobListView(APIView):
    """Listado de jobs de scraping (paginación simple via query params: limit/offset)."""
    def get(self, request):
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        qs = ScrapeJob.objects.all()
        total = qs.count()
        jobs = qs[offset:offset+limit]
        serializer = ScrapeJobSerializer(jobs, many=True)
        return Response({
            'count': total,
            'limit': limit,
            'offset': offset,
            'results': serializer.data
        })


class ScrapeJobDetailView(APIView):
    """Detalle de un job específico."""
    def get(self, request, pk: str):
        try:
            job = ScrapeJob.objects.get(pk=pk)
        except ScrapeJob.DoesNotExist:
            return Response({'error': 'ScrapeJob no encontrado'}, status=404)
        serializer = ScrapeJobSerializer(job)
        return Response(serializer.data)


class ScrapeJobCancelView(APIView):
    """Cancelar un job de scraping en curso (revocar tarea Celery)."""
    def post(self, request, pk: str):
        try:
            job = ScrapeJob.objects.get(pk=pk)
        except ScrapeJob.DoesNotExist:
            return Response({'error': 'ScrapeJob no encontrado'}, status=404)

        if job.status in [ScrapeJob.Status.SUCCESS, ScrapeJob.Status.FAILURE, ScrapeJob.Status.REVOKED]:
            return Response({'error': f'No se puede cancelar un job con estado {job.status}'}, status=400)

        if not job.task_id:
            job.mark_revoked()
            return Response({'status': 'revoked', 'detail': 'Job sin task_id asociado; marcado como REVOKED localmente'})

        try:
            from celery.app.control import Control
            from django.conf import settings as dj_settings
            # Usar la app registrada en celery.py
            from dropship_bot.celery import app as celery_app
            celery_app.control.revoke(job.task_id, terminate=True)
            job.mark_revoked()
            return Response({'status': 'revoked', 'task_id': job.task_id})
        except Exception as e:
            return Response({'error': f'Error al revocar: {e}'}, status=500)
