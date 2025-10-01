from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Product
    """
    list_display = [
        'title', 'price', 'category', 'source_platform', 
        'rating', 'shipping_time', 'created_at'
    ]
    list_filter = [
        'source_platform', 'category', 'created_at', 
        'shipping_time', 'rating'
    ]
    search_fields = ['title', 'category', 'url']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'price', 'url', 'image')
        }),
        ('Detalles del Producto', {
            'fields': ('category', 'rating', 'shipping_time', 'source_platform')
        }),
        ('Metadatos', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar queryset"""
        return super().get_queryset(request).select_related()
