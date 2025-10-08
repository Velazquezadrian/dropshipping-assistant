"""
URLs para la aplicación de productos
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductViewSet,
    HealthCheckViewSet,
    AsyncScrapeLaunchView,
    AsyncScrapeStatusView,
    ScrapeJobListView,
    ScrapeJobDetailView,
    ScrapeJobCancelView,
)
from .analytics_views import (
    DashboardStatsView,
    ScrapingAnalyticsView,
    TrendAnalysisView,
    ProductMetricsView
)
from .dashboard_views import DashboardView, AnalyticsView, SimpleDashboardView, ProductFinderView

# Router de DRF
router = DefaultRouter()
router.register(r'products', ProductViewSet)
router.register(r'health', HealthCheckViewSet, basename='health')

urlpatterns = [
    path('api/', include(router.urls)),
    # Analytics API endpoints
    path('api/dashboard/stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('api/analytics/scraping/', ScrapingAnalyticsView.as_view(), name='scraping-analytics'),
    path('api/analytics/trends/', TrendAnalysisView.as_view(), name='trend-analysis'),
    path('api/analytics/metrics/', ProductMetricsView.as_view(), name='product-metrics'),
    # Async scraping
    path('api/scrape/async/', AsyncScrapeLaunchView.as_view(), name='scrape-async'),
    path('api/scrape/status/<str:task_id>/', AsyncScrapeStatusView.as_view(), name='scrape-async-status'),
    # Scrape jobs history
    path('api/scrapes/jobs/', ScrapeJobListView.as_view(), name='scrape-jobs-list'),
    path('api/scrapes/jobs/<uuid:pk>/', ScrapeJobDetailView.as_view(), name='scrape-jobs-detail'),
    path('api/scrapes/jobs/<uuid:pk>/cancel/', ScrapeJobCancelView.as_view(), name='scrape-jobs-cancel'),
    # HTML Dashboard views
    path('dashboard/', DashboardView.as_view(), name='dashboard-html'),
    path('simple/', SimpleDashboardView.as_view(), name='simple-dashboard'),
    path('analytics/', AnalyticsView.as_view(), name='analytics-html'),
    path('finder/', ProductFinderView.as_view(), name='product-finder'),
]