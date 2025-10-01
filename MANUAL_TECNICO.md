# 🔧 Manual Técnico - Dropship Bot

## Documentación Técnica Completa

Esta documentación está dirigida a desarrolladores, administradores de sistemas y personal técnico que necesitan entender, mantener, modificar o desplegar el sistema Dropship Bot.

---

## 📋 Índice

1. [Arquitectura del Sistema](#arquitectura)
2. [Instalación y Configuración](#instalacion)
3. [Estructura del Código](#estructura)
4. [API Reference](#api)
5. [Base de Datos](#database)
6. [Servicios y Módulos](#servicios)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Monitoreo y Logs](#monitoring)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura del Sistema {#arquitectura}

### Stack Tecnológico

```
Frontend:     Django REST Framework Browsable API
Backend:      Django 5.2.6 + Python 3.8+
Database:     SQLite (desarrollo) / PostgreSQL (producción)
Cache:        Django Cache Framework
Queue:        Django-crontab (desarrollo) / Celery (producción)
Notifications: Telegram Bot API, Discord Webhooks
Testing:      Django TestCase, APITestCase
```

### Diagrama de Arquitectura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Clients   │    │  Notifications  │    │   Schedulers    │
│                 │    │                 │    │                 │
│ - Web Browser   │    │ - Telegram Bot  │    │ - Cron Jobs     │
│ - Mobile Apps   │    │ - Discord       │    │ - Periodic      │
│ - Scripts       │    │   Webhooks      │    │   Scraping      │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Django Application                           │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │   Models    │  │    Views    │  │ Serializers │             │
│  │             │  │             │  │             │             │
│  │ - Product   │  │ - ViewSets  │  │ - DRF       │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  Services   │  │   Filters   │  │   Scrapers  │             │
│  │             │  │             │  │             │             │
│  │ - Managers  │  │ - Query     │  │ - Mock      │             │
│  │ - Notifs    │  │ - List      │  │ - AliExpr   │             │
│  └─────────────┘  └─────────────┘  └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                        ┌─────────────────┐
                        │    Database     │
                        │                 │
                        │ - SQLite/PG     │
                        │ - Products      │
                        │ - Metadata      │
                        └─────────────────┘
```

---

## 🚀 Instalación y Configuración {#instalacion}

### Requisitos del Sistema

```bash
# Requisitos mínimos
- Python 3.8+
- 2GB RAM
- 1GB espacio en disco
- SO: Windows/Linux/macOS

# Requisitos de producción
- Python 3.10+
- 8GB RAM
- 20GB espacio en disco
- PostgreSQL 12+
- Redis 6+ (opcional)
```

### Instalación Paso a Paso

#### 1. Clonar y Configurar Entorno

```bash
git clone [tu-repo]
cd Dropshiping

# Crear entorno virtual
python -m venv .venv

# Activar entorno
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate
```

#### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

**requirements.txt completo:**
```
Django==5.2.6
djangorestframework==3.16.1
django-crontab==0.7.1
django-filter==25.1
requests==2.32.5
python-telegram-bot==22.5

# Para desarrollo
coverage==7.6.9
pytest-django==4.8.0
```

#### 3. Variables de Entorno

Crear `.env` (opcional):
```bash
# Django
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (opcional - por defecto usa SQLite)
DATABASE_URL=postgresql://user:pass@localhost:5432/dropship_db

# Telegram
TELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ
TELEGRAM_CHAT_ID=123456789

# Discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/abc

# Logging
LOG_LEVEL=INFO
LOG_FILE=dropship_bot.log
```

#### 4. Configuración de Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

#### 5. Verificar Instalación

```bash
# Ejecutar tests
python manage.py test products

# Iniciar servidor
python manage.py runserver

# Probar API
curl http://localhost:8000/health/
```

---

## 📁 Estructura del Código {#estructura}

### Estructura de Directorios

```
dropship_bot/
├── dropship_bot/               # Configuración principal
│   ├── __init__.py
│   ├── settings.py            # Configuraciones Django
│   ├── urls.py               # URLs principales
│   ├── wsgi.py               # WSGI application
│   └── asgi.py               # ASGI application (futuro)
│
├── products/                  # App principal
│   ├── __init__.py
│   ├── apps.py               # Configuración de la app
│   ├── models.py             # Modelo Product
│   ├── views.py              # ViewSets DRF
│   ├── serializers.py        # Serializers DRF
│   ├── urls.py               # URLs de la app
│   ├── admin.py              # Admin interface
│   ├── signals.py            # Django signals
│   ├── cron.py               # Tareas programadas
│   ├── tests.py              # Tests unitarios
│   │
│   ├── services/             # Servicios de negocio
│   │   ├── __init__.py
│   │   ├── scraper.py        # Sistema de scraping
│   │   ├── filters.py        # Sistema de filtros
│   │   ├── notifications.py  # Sistema de notificaciones
│   │   └── product_manager.py # Gestión de productos
│   │
│   ├── management/           # Comandos personalizados
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── scrape_products.py
│   │       └── manage_cron.py
│   │
│   └── migrations/           # Migraciones de DB
│       ├── __init__.py
│       └── 0001_initial.py
│
├── static/                   # Archivos estáticos (futuro)
├── media/                    # Archivos de media (futuro)
├── db.sqlite3               # Base de datos SQLite
├── dropship_bot.log         # Archivo de logs
├── requirements.txt         # Dependencias Python
├── README.md               # Documentación principal
├── MANUAL_USUARIO.md       # Manual de usuario
└── MANUAL_TECNICO.md       # Este archivo
```

### Componentes Clave

#### 1. Modelo de Datos (`models.py`)

```python
class Product(models.Model):
    # Campos principales
    title = CharField(max_length=500)           # Título del producto
    price = DecimalField(max_digits=10, decimal_places=2)  # Precio
    url = URLField(unique=True)                 # URL única (idempotencia)
    image = URLField(blank=True, null=True)     # Imagen del producto
    created_at = DateTimeField(default=timezone.now)  # Timestamp
    
    # Campos para filtrado
    shipping_time = PositiveIntegerField(null=True, blank=True)  # Días
    category = CharField(max_length=200, blank=True, null=True)  # Categoría
    rating = DecimalField(max_digits=3, decimal_places=2, null=True, blank=True)  # 0-5
    source_platform = CharField(max_length=100, default='aliexpress')  # Plataforma
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
```

#### 2. API Views (`views.py`)

```python
class ProductViewSet(viewsets.ModelViewSet):
    """ViewSet principal para productos"""
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    
    # Acciones personalizadas
    @action(detail=False, methods=['get'])
    def stats(self, request): ...
    
    @action(detail=False, methods=['get'])
    def recent(self, request): ...
```

---

## 🔌 API Reference {#api}

### Endpoints Principales

#### Products CRUD

```
GET    /api/products/           # Listar productos
POST   /api/products/           # Crear producto
GET    /api/products/{id}/      # Obtener producto
PUT    /api/products/{id}/      # Actualizar producto completo
PATCH  /api/products/{id}/      # Actualizar producto parcial
DELETE /api/products/{id}/      # Eliminar producto
```

#### Endpoints Especiales

```
GET /api/products/stats/                    # Estadísticas generales
GET /api/products/recent/                   # Productos últimas 24h
GET /api/products/by_platform/?platform=X  # Productos por plataforma
```

#### Health Check

```
GET /health/                    # Health check simple
GET /api/health/status/         # Health check detallado
```

### Parámetros de Filtrado

| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `min_price` | Decimal | Precio mínimo | `?min_price=10.50` |
| `max_price` | Decimal | Precio máximo | `?max_price=100.00` |
| `keywords` | String | Palabras clave (CSV) | `?keywords=phone,smart` |
| `max_shipping_days` | Integer | Días máximos de envío | `?max_shipping_days=15` |
| `min_rating` | Decimal | Calificación mínima | `?min_rating=4.0` |
| `platforms` | String | Plataformas (CSV) | `?platforms=ali,amazon` |
| `categories` | String | Categorías (CSV) | `?categories=Electronics` |
| `search` | String | Búsqueda en título/categoría | `?search=bluetooth` |
| `ordering` | String | Ordenamiento | `?ordering=-price` |
| `page` | Integer | Página | `?page=2` |
| `page_size` | Integer | Tamaño de página | `?page_size=50` |

### Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| 200 | OK - Solicitud exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 404 | Not Found - Recurso no encontrado |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Health check falló |

### Ejemplos de Respuesta

#### Lista de Productos
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Smartphone Android",
            "price": "299.99",
            "url": "https://example.com/product1",
            "image": "https://example.com/image1.jpg",
            "created_at": "2025-09-29T10:30:00Z",
            "shipping_time": 15,
            "category": "Electronics",
            "rating": "4.5",
            "source_platform": "mock_aliexpress"
        }
    ]
}
```

#### Estadísticas
```json
{
    "total_products": 150,
    "average_price": "45.67",
    "min_price": "5.99",
    "max_price": "299.99",
    "platforms": ["mock_aliexpress", "aliexpress"],
    "categories": ["Electronics", "Home & Garden"],
    "products_today": 25,
    "products_this_week": 89
}
```

---

## 🗄️ Base de Datos {#database}

### Esquema de Base de Datos

```sql
-- Tabla principal: products_product
CREATE TABLE products_product (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    url VARCHAR(200) UNIQUE NOT NULL,
    image VARCHAR(200),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    shipping_time INTEGER CHECK (shipping_time >= 0),
    category VARCHAR(200),
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    source_platform VARCHAR(100) DEFAULT 'aliexpress'
);

-- Índices para performance
CREATE INDEX idx_products_created_at ON products_product(created_at DESC);
CREATE INDEX idx_products_price ON products_product(price);
CREATE INDEX idx_products_platform ON products_product(source_platform);
CREATE INDEX idx_products_category ON products_product(category);
CREATE INDEX idx_products_rating ON products_product(rating);
```

### Migraciones

```bash
# Crear migración
python manage.py makemigrations products

# Aplicar migraciones
python manage.py migrate

# Ver migraciones
python manage.py showmigrations

# Deshacer migración (cuidado!)
python manage.py migrate products 0001
```

### Backup y Restore

```bash
# Backup SQLite
cp db.sqlite3 backup_$(date +%Y%m%d_%H%M%S).sqlite3

# Backup PostgreSQL
pg_dump dropship_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore PostgreSQL
psql dropship_db < backup_20250929_103000.sql
```

---

## ⚙️ Servicios y Módulos {#servicios}

### 1. Sistema de Scraping (`services/scraper.py`)

#### Estructura de Clases

```python
BaseScraper (ABC)
├── MockScraper          # Para testing y desarrollo
├── AliExpressScraper    # Para AliExpress (básico)
└── [FutureScraper]      # Amazon, eBay, etc.

ScraperFactory           # Factory pattern
```

#### Agregar Nuevo Scraper

```python
class AmazonScraper(BaseScraper):
    def scrape_products(self, **kwargs):
        # Implementar lógica de scraping
        pass
    
    def get_platform_name(self):
        return 'amazon'

# Registrar en Factory
ScraperFactory.scrapers['amazon'] = AmazonScraper
```

### 2. Sistema de Filtros (`services/filters.py`)

#### Uso Programático

```python
from products.services.filters import ProductFilter

# Crear filtro
filter = ProductFilter()
filter.add_price_filter(min_price=20, max_price=100)
filter.add_keyword_filter(['smartphone', 'android'])

# Aplicar a QuerySet
filtered_qs = filter.filter_queryset(Product.objects.all())

# Aplicar a lista
filtered_list = filter.filter_product_list(product_list)
```

### 3. Gestión de Productos (`services/product_manager.py`)

#### Funciones Principales

```python
# Crear producto con validación
product, created = ProductManager.create_or_update_product(data)

# Importación en lotes
stats = ProductManager.bulk_create_or_update_products(products_data)

# Validar datos
validated_data = ProductManager.validate_product_data(raw_data)

# Deduplicar
removed_count = ProductManager.deduplicate_products()
```

### 4. Notificaciones (`services/notifications.py`)

#### Configuración

```python
# settings.py
TELEGRAM_BOT_TOKEN = 'tu_token'
TELEGRAM_CHAT_ID = 'tu_chat_id'
DISCORD_WEBHOOK_URL = 'tu_webhook_url'
```

#### Uso

```python
from products.services.notifications import notification_manager

# Notificar producto individual
results = notification_manager.notify_new_product(product)

# Notificar múltiples productos
results = notification_manager.notify_bulk_products(products)

# Probar notificaciones
results = notification_manager.test_notifications()
```

---

## 🧪 Testing {#testing}

### Estructura de Tests

```
products/tests.py
├── ProductModelTest      # Tests del modelo
├── ScraperTest          # Tests de scraping
├── FilterTest           # Tests de filtros
├── ProductManagerTest   # Tests de gestión
├── APITest             # Tests de API
├── NotificationTest    # Tests de notificaciones
└── IntegrationTest     # Tests de integración
```

### Ejecutar Tests

```bash
# Todos los tests
python manage.py test products

# Tests específicos
python manage.py test products.tests.ProductModelTest

# Con verbosidad
python manage.py test products --verbosity=2

# Con coverage
coverage run --source='.' manage.py test products
coverage report
coverage html  # Genera reporte HTML
```

### Escribir Nuevos Tests

```python
class MyFeatureTest(TestCase):
    def setUp(self):
        """Configuración antes de cada test"""
        self.product = Product.objects.create(
            title="Test Product",
            price=Decimal("29.99"),
            url="https://example.com/test"
        )
    
    def test_my_feature(self):
        """Test de mi nueva funcionalidad"""
        # Arrange
        expected_result = "expected"
        
        # Act
        result = my_function(self.product)
        
        # Assert
        self.assertEqual(result, expected_result)
```

### Mocking para Tests

```python
from unittest.mock import patch, MagicMock

@patch('requests.post')
def test_notification(self, mock_post):
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response
    
    # Tu test aquí
    result = send_notification("test message")
    self.assertTrue(result)
```

---

## 🚀 Deployment {#deployment}

### Desarrollo Local

```bash
# Activar entorno
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instalar dependencias
pip install -r requirements.txt

# Configurar DB
python manage.py migrate

# Ejecutar servidor
python manage.py runserver 0.0.0.0:8000
```

### Producción con Docker

#### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dropship_bot.wsgi:application"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@db:5432/dropship
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: dropship
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  postgres_data:
```

### Configuración de Producción

#### settings/production.py

```python
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['tu-dominio.com', 'www.tu-dominio.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Security
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 📊 Monitoreo y Logs {#monitoring}

### Configuración de Logging

```python
# settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs/dropship_bot.log',
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'products': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Métricas Importantes

#### Health Check Personalizado

```python
def custom_health_check():
    """Health check personalizado"""
    checks = {
        'database': check_database(),
        'external_apis': check_external_apis(),
        'disk_space': check_disk_space(),
        'memory': check_memory_usage(),
    }
    
    return {
        'status': 'ok' if all(checks.values()) else 'error',
        'checks': checks,
        'timestamp': timezone.now()
    }
```

#### Monitoreo con Scripts

```bash
#!/bin/bash
# monitor.sh

# Health check
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/)

if [ $response -ne 200 ]; then
    echo "ALERT: Health check failed with status $response"
    # Enviar alerta
fi

# Check disk space
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -gt 80 ]; then
    echo "ALERT: Disk usage is at ${disk_usage}%"
fi
```

### Integración con Sentry (Producción)

```python
# settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="https://tu-dsn@sentry.io/proyecto",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

---

## 🔧 Troubleshooting {#troubleshooting}

### Problemas Comunes

#### 1. Error: "No module named 'products'"

**Causa**: Python no encuentra el módulo
**Solución**:
```bash
# Verificar PYTHONPATH
echo $PYTHONPATH

# Verificar estructura
ls -la products/

# Verificar __init__.py
ls products/__init__.py
```

#### 2. Error: "CSRF token missing"

**Causa**: Falta token CSRF en requests POST
**Solución**:
```python
# En tests
from django.test import Client
client = Client(enforce_csrf_checks=False)

# En API calls
headers = {'X-CSRFToken': csrf_token}
```

#### 3. Error: "Database is locked"

**Causa**: SQLite bloqueado por otro proceso
**Solución**:
```bash
# Verificar procesos
ps aux | grep python

# Matar procesos Django
pkill -f "manage.py runserver"

# Reiniciar servidor
python manage.py runserver
```

#### 4. Notificaciones no funcionan

**Diagnóstico**:
```python
# Test desde shell
python manage.py shell
>>> from products.services.notifications import notification_manager
>>> result = notification_manager.test_notifications()
>>> print(result)
```

### Debugging

#### Django Debug Toolbar (Desarrollo)

```python
# settings/development.py
if DEBUG:
    import debug_toolbar
    
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
    DEBUG_TOOLBAR_CONFIG = {
        'SHOW_TOOLBAR_CALLBACK': lambda request: True,
    }
```

#### Logging de Debug

```python
import logging
logger = logging.getLogger('products')

def my_function():
    logger.debug("Entrando a my_function")
    logger.info("Procesando datos")
    logger.warning("Advertencia")
    logger.error("Error específico")
```

### Performance

#### Optimización de Queries

```python
# Usar select_related para ForeignKey
products = Product.objects.select_related('category').all()

# Usar prefetch_related para ManyToMany
products = Product.objects.prefetch_related('tags').all()

# Optimizar filtros
products = Product.objects.filter(
    price__gte=20,
    price__lte=100
).order_by('-created_at')[:20]
```

#### Cache de Queries

```python
from django.core.cache import cache

def get_product_stats():
    cache_key = 'product_stats'
    stats = cache.get(cache_key)
    
    if stats is None:
        stats = calculate_stats()
        cache.set(cache_key, stats, 300)  # 5 minutos
    
    return stats
```

---

## 🔐 Seguridad

### Configuraciones de Seguridad

```python
# settings/production.py

# HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Headers de seguridad
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HSTS
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Cookies
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Rate Limiting

```python
# Con django-ratelimit
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h', method='GET')
def api_view(request):
    pass
```

---

## 📈 Escalabilidad

### Optimizaciones para Alto Volumen

#### 1. Database Sharding
```python
class DatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'products':
            return 'products_db'
        return None
```

#### 2. Async Views (Django 4.1+)
```python
from django.http import JsonResponse
import asyncio

async def async_api_view(request):
    data = await fetch_data_async()
    return JsonResponse(data)
```

#### 3. Background Tasks con Celery
```python
# tasks.py
from celery import shared_task

@shared_task
def scrape_products_async():
    from products.cron import scrape_products
    return scrape_products()
```

---

## 📝 API Documentation

### Swagger/OpenAPI

```python
# settings.py
INSTALLED_APPS += ['drf_yasg']

# urls.py
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="Dropship Bot API",
        default_version='v1',
        description="API para gestión de productos de dropshipping",
    ),
    public=True,
)

urlpatterns += [
    path('swagger/', schema_view.with_ui('swagger')),
    path('redoc/', schema_view.with_ui('redoc')),
]
```

---

## 🤝 Contribución

### Guías de Contribución

#### 1. Código
- Seguir PEP 8
- Documentar funciones con docstrings
- Agregar tests para nuevas funcionalidades
- Usar type hints cuando sea posible

#### 2. Git Workflow
```bash
# Crear branch
git checkout -b feature/nueva-funcionalidad

# Commits descriptivos
git commit -m "feat: agregar scraper para Amazon"

# Pull request
git push origin feature/nueva-funcionalidad
```

#### 3. Testing
- Cobertura mínima del 80%
- Tests unitarios para cada función
- Tests de integración para workflows completos

---

**Documentación actualizada: Septiembre 2025**
**Versión del sistema: 1.0.0**