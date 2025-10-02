"""
Vistas HTML para el dashboard de analytics
"""

from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


class DashboardView(TemplateView):
    """
    Vista principal del dashboard
    """
    template_name = 'products/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard de Productos'
        return context


class AnalyticsView(TemplateView):
    """
    Vista de analytics avanzados
    """
    template_name = 'products/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Analytics de Scraping'
        return context