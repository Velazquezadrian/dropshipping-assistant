"""
Vistas específicas para analytics y dashboard de productos
"""

import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Avg, Min, Max, Count, Sum, Q
from django.db.models.functions import TruncDate, TruncHour
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from collections import defaultdict, Counter

from .models import Product
from .serializers import ProductSerializer

logger = logging.getLogger('products')


class DashboardStatsView(APIView):
    """
    Vista para estadísticas del dashboard principal
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Obtiene estadísticas completas para el dashboard
        """
        try:
            now = timezone.now()
            today = now.date()
            yesterday = now - timedelta(days=1)
            week_ago = now - timedelta(days=7)
            month_ago = now - timedelta(days=30)

            # Estadísticas básicas
            total_products = Product.objects.count()
            products_today = Product.objects.filter(created_at__date=today).count()
            products_yesterday = Product.objects.filter(
                created_at__date=yesterday.date()
            ).count()
            products_this_week = Product.objects.filter(created_at__gte=week_ago).count()
            products_this_month = Product.objects.filter(created_at__gte=month_ago).count()

            # Estadísticas de precios
            price_stats = Product.objects.aggregate(
                avg_price=Avg('price'),
                min_price=Min('price'),
                max_price=Max('price'),
                total_value=Sum('price')
            )

            # Estadísticas por categoría
            category_stats = list(
                Product.objects.values('category')
                .annotate(
                    count=Count('id'),
                    avg_price=Avg('price'),
                    avg_rating=Avg('rating')
                )
                .order_by('-count')[:10]
            )

            # Estadísticas por plataforma
            platform_stats = list(
                Product.objects.values('source_platform')
                .annotate(
                    count=Count('id'),
                    avg_price=Avg('price'),
                    avg_rating=Avg('rating')
                )
                .order_by('-count')
            )

            # Productos por día (últimos 7 días)
            daily_stats = list(
                Product.objects.filter(created_at__gte=week_ago)
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            # Productos por hora (últimas 24 horas)
            hourly_stats = list(
                Product.objects.filter(created_at__gte=yesterday)
                .annotate(hour=TruncHour('created_at'))
                .values('hour')
                .annotate(count=Count('id'))
                .order_by('hour')
            )

            # Top productos por rating
            top_rated_products = list(
                Product.objects.filter(rating__gte=4.0)
                .order_by('-rating', '-created_at')[:10]
                .values('title', 'price', 'rating', 'category', 'source_platform')
            )

            # Productos más baratos
            cheapest_products = list(
                Product.objects.filter(price__gt=0)
                .order_by('price')[:10]
                .values('title', 'price', 'rating', 'category', 'source_platform')
            )

            # Productos más caros
            expensive_products = list(
                Product.objects.order_by('-price')[:10]
                .values('title', 'price', 'rating', 'category', 'source_platform')
            )

            # Cambio porcentual desde ayer
            change_from_yesterday = 0
            if products_yesterday > 0:
                change_from_yesterday = ((products_today - products_yesterday) / products_yesterday) * 100

            data = {
                'summary': {
                    'total_products': total_products,
                    'products_today': products_today,
                    'products_yesterday': products_yesterday,
                    'products_this_week': products_this_week,
                    'products_this_month': products_this_month,
                    'change_from_yesterday': round(change_from_yesterday, 2),
                    'average_price': round(price_stats['avg_price'] or 0, 2),
                    'min_price': round(price_stats['min_price'] or 0, 2),
                    'max_price': round(price_stats['max_price'] or 0, 2),
                    'total_value': round(price_stats['total_value'] or 0, 2),
                },
                'charts': {
                    'daily_products': daily_stats,
                    'hourly_products': hourly_stats,
                    'category_distribution': category_stats,
                    'platform_distribution': platform_stats,
                },
                'top_lists': {
                    'top_rated': top_rated_products,
                    'cheapest': cheapest_products,
                    'most_expensive': expensive_products,
                },
                'last_updated': now
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del dashboard: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ScrapingAnalyticsView(APIView):
    """
    Vista para analytics específicos del scraping
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Obtiene métricas específicas del proceso de scraping
        """
        try:
            now = timezone.now()
            last_24h = now - timedelta(hours=24)
            last_week = now - timedelta(days=7)
            last_month = now - timedelta(days=30)

            # Actividad de scraping por período
            scraping_activity = {
                'last_24h': Product.objects.filter(created_at__gte=last_24h).count(),
                'last_week': Product.objects.filter(created_at__gte=last_week).count(),
                'last_month': Product.objects.filter(created_at__gte=last_month).count(),
            }

            # Promedio de productos por hora en las últimas 24h
            hourly_avg = scraping_activity['last_24h'] / 24 if scraping_activity['last_24h'] > 0 else 0

            # Éxito del scraping por plataforma
            platform_success = {}
            for platform_data in Product.objects.values('source_platform').annotate(count=Count('id')):
                platform = platform_data['source_platform']
                count = platform_data['count']
                
                # Calcular tasa de éxito basada en productos con datos completos
                complete_products = Product.objects.filter(
                    source_platform=platform,
                    title__isnull=False,
                    price__gt=0,
                    url__isnull=False
                ).count()
                
                success_rate = (complete_products / count * 100) if count > 0 else 0
                
                platform_success[platform] = {
                    'total_products': count,
                    'complete_products': complete_products,
                    'success_rate': round(success_rate, 2)
                }

            # Tiempo de respuesta del scraper (simulado basado en timestamps)
            recent_products = Product.objects.filter(created_at__gte=last_24h).order_by('created_at')
            
            response_times = []
            if recent_products.count() > 1:
                for i in range(1, min(len(recent_products), 100)):  # Últimos 100 para simular
                    time_diff = (recent_products[i].created_at - recent_products[i-1].created_at).total_seconds()
                    if time_diff < 300:  # Solo si es menos de 5 minutos (scraping continuo)
                        response_times.append(time_diff)

            avg_response_time = sum(response_times) / len(response_times) if response_times else 0

            # Categorías más scrapeadas
            top_categories = list(
                Product.objects.filter(created_at__gte=last_week)
                .values('category')
                .annotate(count=Count('id'))
                .order_by('-count')[:10]
            )

            # Calidad de datos
            data_quality = {
                'products_with_images': Product.objects.exclude(image='').count(),
                'products_with_ratings': Product.objects.filter(rating__gt=0).count(),
                'products_with_shipping_info': Product.objects.filter(shipping_time__gt=0).count(),
                'total_products': Product.objects.count()
            }

            # Calcular porcentajes de calidad
            total = data_quality['total_products']
            if total > 0:
                data_quality['image_completion'] = round((data_quality['products_with_images'] / total) * 100, 2)
                data_quality['rating_completion'] = round((data_quality['products_with_ratings'] / total) * 100, 2)
                data_quality['shipping_completion'] = round((data_quality['products_with_shipping_info'] / total) * 100, 2)

            data = {
                'scraping_activity': scraping_activity,
                'performance': {
                    'hourly_average': round(hourly_avg, 2),
                    'avg_response_time': round(avg_response_time, 2),
                    'platform_success_rates': platform_success
                },
                'data_quality': data_quality,
                'top_categories': top_categories,
                'last_updated': now
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Error obteniendo analytics de scraping: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TrendAnalysisView(APIView):
    """
    Vista para análisis de tendencias de productos
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Obtiene análisis de tendencias
        """
        try:
            days = int(request.query_params.get('days', 7))
            if days > 90:
                days = 90  # Límite máximo
            
            start_date = timezone.now() - timedelta(days=days)

            # Tendencias de categorías
            category_trends = defaultdict(list)
            category_data = (
                Product.objects.filter(created_at__gte=start_date)
                .annotate(date=TruncDate('created_at'))
                .values('date', 'category')
                .annotate(count=Count('id'))
                .order_by('date', 'category')
            )

            for item in category_data:
                category_trends[item['category']].append({
                    'date': item['date'],
                    'count': item['count']
                })

            # Tendencias de precios por categoría
            price_trends = {}
            for category in category_trends.keys():
                prices = list(
                    Product.objects.filter(
                        created_at__gte=start_date,
                        category=category
                    )
                    .annotate(date=TruncDate('created_at'))
                    .values('date')
                    .annotate(avg_price=Avg('price'))
                    .order_by('date')
                )
                price_trends[category] = prices

            # Productos en tendencia (más scrapeados recientemente)
            trending_terms = []
            recent_titles = Product.objects.filter(
                created_at__gte=start_date
            ).values_list('title', flat=True)

            # Análisis básico de palabras clave
            word_counts = Counter()
            for title in recent_titles:
                words = title.lower().split()
                # Filtrar palabras comunes y obtener palabras relevantes
                relevant_words = [
                    word for word in words 
                    if len(word) > 3 and word not in ['with', 'from', 'this', 'that', 'fast', 'free']
                ]
                word_counts.update(relevant_words[:3])  # Solo primeras 3 palabras relevantes

            trending_terms = word_counts.most_common(10)

            # Análisis de velocidad de scraping
            scraping_velocity = list(
                Product.objects.filter(created_at__gte=start_date)
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date')
            )

            data = {
                'period_days': days,
                'category_trends': dict(category_trends),
                'price_trends': price_trends,
                'trending_keywords': trending_terms,
                'scraping_velocity': scraping_velocity,
                'analysis_date': timezone.now()
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Error obteniendo análisis de tendencias: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductMetricsView(APIView):
    """
    Vista para métricas detalladas de productos
    """
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        """
        Obtiene métricas detalladas por categoría, plataforma, etc.
        """
        try:
            # Métricas por rango de precios
            price_ranges = [
                {'min': 0, 'max': 10, 'label': '$0-$10'},
                {'min': 10, 'max': 25, 'label': '$10-$25'},
                {'min': 25, 'max': 50, 'label': '$25-$50'},
                {'min': 50, 'max': 100, 'label': '$50-$100'},
                {'min': 100, 'max': 999999, 'label': '$100+'}
            ]

            price_distribution = []
            for price_range in price_ranges:
                count = Product.objects.filter(
                    price__gte=price_range['min'],
                    price__lt=price_range['max']
                ).count()
                
                price_distribution.append({
                    'range': price_range['label'],
                    'count': count
                })

            # Métricas por rating
            rating_distribution = []
            for rating in [1, 2, 3, 4, 5]:
                count = Product.objects.filter(
                    rating__gte=rating,
                    rating__lt=rating + 1
                ).count()
                
                rating_distribution.append({
                    'rating': f"{rating}★",
                    'count': count
                })

            # Métricas de shipping
            shipping_ranges = [
                {'min': 0, 'max': 7, 'label': '1-7 días'},
                {'min': 7, 'max': 15, 'label': '7-15 días'},
                {'min': 15, 'max': 30, 'label': '15-30 días'},
                {'min': 30, 'max': 999, 'label': '30+ días'}
            ]

            shipping_distribution = []
            for ship_range in shipping_ranges:
                count = Product.objects.filter(
                    shipping_time__gte=ship_range['min'],
                    shipping_time__lt=ship_range['max']
                ).count()
                
                shipping_distribution.append({
                    'range': ship_range['label'],
                    'count': count
                })

            # Top palabras clave en títulos
            all_titles = Product.objects.values_list('title', flat=True)
            keyword_counts = Counter()
            
            for title in all_titles:
                words = title.lower().split()
                keywords = [word for word in words if len(word) > 4]
                keyword_counts.update(keywords)

            top_keywords = keyword_counts.most_common(20)

            data = {
                'price_distribution': price_distribution,
                'rating_distribution': rating_distribution,
                'shipping_distribution': shipping_distribution,
                'top_keywords': top_keywords,
                'generated_at': timezone.now()
            }

            return Response(data)

        except Exception as e:
            logger.error(f"Error obteniendo métricas de productos: {e}")
            return Response(
                {'error': 'Error interno del servidor'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )