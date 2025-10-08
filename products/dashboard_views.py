"""
Vistas HTML para el dashboard de analytics
"""

from django.shortcuts import render
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.utils import timezone
from .models import Product
from .services.scraper import AliExpressScraper
from django import forms


class ProductFinderForm(forms.Form):
    min_price = forms.DecimalField(required=False, min_value=0, label="Precio mín", decimal_places=2)
    max_price = forms.DecimalField(required=False, min_value=0, label="Precio máx", decimal_places=2)
    min_rating = forms.DecimalField(required=False, min_value=0, max_value=5, decimal_places=1, label="Rating mín")
    category = forms.CharField(required=False, max_length=100, label="Categoría contiene")
    max_shipping_days = forms.IntegerField(required=False, min_value=1, label="Envío máx (días)")
    source = forms.ChoiceField(required=False, choices=[('aliexpress','AliExpress')], initial='aliexpress', label="Fuente")
    search_term = forms.CharField(required=False, max_length=100, label="Buscar texto")


class ProductFinderView(TemplateView):
    template_name = 'products/product_finder.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        form = ProductFinderForm(self.request.GET or None)
        ctx['form'] = form
        ctx['results'] = []
        ctx['error'] = None
        if self.request.GET.get('run') == '1' and form.is_valid():
            scraper = AliExpressScraper()
            search_term = form.cleaned_data.get('search_term') or 'electronics'
            try:
                products = scraper.scrape_products(search_term=search_term, count=20)
                # Filtros en memoria
                filtered = []
                for p in products:
                    if form.cleaned_data.get('min_price') and p['price'] < form.cleaned_data['min_price']:
                        continue
                    if form.cleaned_data.get('max_price') and p['price'] > form.cleaned_data['max_price']:
                        continue
                    if form.cleaned_data.get('min_rating') and p['rating'] < form.cleaned_data['min_rating']:
                        continue
                    if form.cleaned_data.get('category') and form.cleaned_data['category'].lower() not in p['category'].lower():
                        continue
                    if form.cleaned_data.get('max_shipping_days') and p['shipping_time'] and p['shipping_time'] > form.cleaned_data['max_shipping_days']:
                        continue
                    filtered.append(p)
                ctx['results'] = filtered
            except Exception as e:
                ctx['error'] = str(e)
        return ctx


class DashboardView(TemplateView):
    """
    Vista principal del dashboard
    """
    template_name = 'products/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Dashboard de Productos'
        return context


class SimpleDashboardView(ListView):
    """
    Vista simple del dashboard que funciona sin JavaScript
    """
    model = Product
    template_name = 'products/simple_dashboard.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.all().order_by('-created_at')
        
        # Filtros
        max_price = self.request.GET.get('max_price')
        min_rating = self.request.GET.get('min_rating')
        category = self.request.GET.get('category')
        
        if max_price:
            try:
                queryset = queryset.filter(price__lte=float(max_price))
            except (ValueError, TypeError):
                pass
                
        if min_rating:
            try:
                queryset = queryset.filter(rating__gte=float(min_rating))
            except (ValueError, TypeError):
                pass
                
        if category:
            queryset = queryset.filter(category__icontains=category)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Estadísticas básicas
        all_products = Product.objects.all()
        context['total_products'] = all_products.count()
        context['avg_price'] = all_products.aggregate(avg=Avg('price'))['avg'] or 0
        context['products_today'] = all_products.filter(created_at__date=timezone.now().date()).count()
        context['platforms'] = all_products.values_list('source_platform', flat=True).distinct()
        context['categories'] = all_products.exclude(category__isnull=True).exclude(category='').values_list('category', flat=True).distinct()
        
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