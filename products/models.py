from django.db import models
from django.utils import timezone
import uuid
from django.core.validators import MinValueValidator


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


class ScrapeJob(models.Model):
    """Historial de ejecuciones de scraping (asincrónicas o manuales)."""
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        STARTED = 'STARTED', 'Started'
        SUCCESS = 'SUCCESS', 'Success'
        FAILURE = 'FAILURE', 'Failure'
        REVOKED = 'REVOKED', 'Revoked'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_id = models.CharField(max_length=255, blank=True, null=True, help_text="ID real de la tarea Celery")
    query = models.CharField(max_length=300, help_text="Término de búsqueda")
    source = models.CharField(max_length=100, help_text="Scraper usado")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    requested_pages = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    returned_items = models.PositiveIntegerField(default=0)
    created_items = models.PositiveIntegerField(default=0)
    progress = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text="Porcentaje 0-100")
    error = models.TextField(blank=True, null=True)
    meta = models.JSONField(default=dict, blank=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Scrape Job"
        verbose_name_plural = "Scrape Jobs"

    def mark_started(self):
        self.status = self.Status.STARTED
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])

    def update_progress(self, progress: float, processed: int = None, created: int = None, total: int = None):
        self.progress = progress
        if processed is not None:
            self.returned_items = processed
        if created is not None:
            self.created_items = created
        if total is not None and total > 0:
            self.meta['total'] = total
        self.save(update_fields=['progress', 'returned_items', 'created_items', 'meta'])

    def mark_success(self, returned: int, created: int, requested_pages: int, summary: dict):
        self.status = self.Status.SUCCESS
        self.returned_items = returned
        self.created_items = created
        self.requested_pages = requested_pages
        self.progress = 100
        self.finished_at = timezone.now()
        self.meta.update(summary)
        self.save(update_fields=['status', 'returned_items', 'created_items', 'requested_pages', 'progress', 'finished_at', 'meta'])

    def mark_failure(self, error_message: str):
        self.status = self.Status.FAILURE
        self.error = error_message[:2000]
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'error', 'finished_at'])

    def mark_revoked(self):
        self.status = self.Status.REVOKED
        self.finished_at = timezone.now()
        self.save(update_fields=['status', 'finished_at'])

    def duration_seconds(self):
        if self.started_at and self.finished_at:
            return (self.finished_at - self.started_at).total_seconds()
        if self.started_at:
            return (timezone.now() - self.started_at).total_seconds()
        return 0

    def __str__(self):
        return f"ScrapeJob({self.query} - {self.status})"
