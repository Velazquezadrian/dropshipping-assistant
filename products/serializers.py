"""
Serializers para la API REST de productos
"""

from rest_framework import serializers
from .models import Product, ScrapeJob


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Product
    """
    is_recently_added = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
            'url',
            'image',
            'created_at',
            'shipping_time',
            'category',
            'rating',
            'source_platform',
            'is_recently_added'
        ]
        read_only_fields = ['id', 'created_at', 'is_recently_added']
    
    def validate_price(self, value):
        """Validar que el precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero")
        return value
    
    def validate_rating(self, value):
        """Validar que la calificación esté en el rango correcto"""
        if value is not None and (value < 0 or value > 5):
            raise serializers.ValidationError("La calificación debe estar entre 0 y 5")
        return value
    
    def validate_shipping_time(self, value):
        """Validar que el tiempo de envío sea razonable"""
        if value is not None and (value < 0 or value > 365):
            raise serializers.ValidationError("El tiempo de envío debe estar entre 0 y 365 días")
        return value


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear productos (sin campos de solo lectura)
    """
    
    class Meta:
        model = Product
        fields = [
            'title',
            'price',
            'url',
            'image',
            'shipping_time',
            'category',
            'rating',
            'source_platform'
        ]
    
    def validate_price(self, value):
        """Validar que el precio sea positivo"""
        if value <= 0:
            raise serializers.ValidationError("El precio debe ser mayor que cero")
        return value
    
    def validate_rating(self, value):
        """Validar que la calificación esté en el rango correcto"""
        if value is not None and (value < 0 or value > 5):
            raise serializers.ValidationError("La calificación debe estar entre 0 y 5")
        return value


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer simplificado para listado de productos
    """
    
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'price',
            'url',
            'image',
            'created_at',
            'rating',
            'source_platform'
        ]


class ProductStatsSerializer(serializers.Serializer):
    """
    Serializer para estadísticas de productos
    """
    total_products = serializers.IntegerField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    platforms = serializers.ListField(child=serializers.CharField())
    categories = serializers.ListField(child=serializers.CharField())
    products_today = serializers.IntegerField()
    products_this_week = serializers.IntegerField()


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer para el health check
    """
    status = serializers.CharField()
    timestamp = serializers.DateTimeField()
    database = serializers.CharField()
    products_count = serializers.IntegerField()
    last_scrape = serializers.DateTimeField(allow_null=True)


class ScrapeJobSerializer(serializers.ModelSerializer):
    duration_seconds = serializers.SerializerMethodField()

    class Meta:
        model = ScrapeJob
        fields = [
            'id', 'task_id', 'query', 'source', 'status', 'requested_pages',
            'returned_items', 'created_items', 'progress', 'error', 'meta',
            'started_at', 'finished_at', 'created_at', 'duration_seconds'
        ]
        read_only_fields = fields

    def get_duration_seconds(self, obj):  # pragma: no cover simple accessor
        return obj.duration_seconds()