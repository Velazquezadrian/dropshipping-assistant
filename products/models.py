from django.db import models
from django.utils import timezone


class Product(models.Model):
    """
    Modelo para almacenar información de productos de dropshipping
    """
    title = models.CharField(max_length=500, help_text="Título del producto")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Precio del producto")
    url = models.URLField(unique=True, help_text="URL única del producto para evitar duplicados")
    image = models.URLField(blank=True, null=True, help_text="URL de la imagen del producto")
    created_at = models.DateTimeField(default=timezone.now, help_text="Fecha de creación")
    
    # Campos adicionales para filtrado
    shipping_time = models.PositiveIntegerField(
        null=True, blank=True, 
        help_text="Tiempo de envío en días"
    )
    category = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="Categoría del producto"
    )
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True,
        help_text="Calificación del producto (0.00 - 5.00)"
    )
    source_platform = models.CharField(
        max_length=100, default='aliexpress',
        help_text="Plataforma de origen del producto"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
    
    def __str__(self):
        return f"{self.title} - ${self.price}"
    
    def is_recently_added(self):
        """Verifica si el producto fue agregado en las últimas 24 horas"""
        from datetime import timedelta
        return self.created_at >= timezone.now() - timedelta(hours=24)
