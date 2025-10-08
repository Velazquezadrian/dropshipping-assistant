# Manual Técnico - Dropship Bot# 🔧 Manual Técnico - Dropship Bot



## 🏗️ Arquitectura del Sistema## Documentación Técnica Completa



### Visión GeneralEsta documentación está dirigida a desarrolladores, administradores de sistemas y personal técnico que necesitan entender, mantener, modificar o desplegar el sistema Dropship Bot.

Sistema de dropshipping modular construido con Django 5.2.6 que proporciona scraping real de AliExpress, filtrado inteligente y API REST completa con interfaz web.

---

### Componentes Principales

## 📋 Índice

```

dropship_bot/1. [Arquitectura del Sistema](#arquitectura)

├── dropship_bot/          # Configuración principal Django2. [Instalación y Configuración](#instalacion)

│   ├── settings.py        # Configuración del proyecto  3. [Estructura del Código](#estructura)

│   ├── urls.py           # URLs principales4. [API Reference](#api)

│   └── wsgi.py           # WSGI para despliegue5. [Base de Datos](#database)

├── products/             # App principal de productos6. [Servicios y Módulos](#servicios)

│   ├── models.py         # Modelos de datos7. [Scraping Asíncrono](#async-scraping)

│   ├── views.py          # Vistas tradicionales8. [Dashboard y Analytics](#dashboard)

│   ├── real_views.py     # Vistas para bot real9. [Sistema de Notificaciones](#notifications)

│   ├── serializers.py    # Serializadores DRF10. [Testing](#testing)

│   ├── urls.py           # URLs de productos11. [Deployment con Docker](#deployment)

│   └── services/         # Lógica de negocio12. [Monitoreo y Logs](#monitoring)

│       ├── real_aliexpress_bot.py  # Bot real de AliExpress13. [Troubleshooting](#troubleshooting)

│       ├── scraper.py              # Scraper base

│       ├── notifications.py        # Sistema de notificaciones---

│       └── filters.py              # Filtros de productos

├── templates/            # Templates HTML## 🏗️ Arquitectura del Sistema {#arquitectura}

│   └── real_filter.html  # Interfaz web principal

├── static/              # Archivos estáticos### Stack Tecnológico

├── certs/               # Certificados SSL

└── requirements.txt     # Dependencias```

```Frontend:     Django Templates + Bootstrap 5 + Chart.js

Backend:      Django 5.2.6 + Python 3.13

## 🔧 Componentes TécnicosDatabase:     SQLite (desarrollo) / PostgreSQL (producción)

Cache:        Redis (producción)

### 1. Bot Real de AliExpressQueue:        Celery + Redis (producción)

**Archivo**: `products/services/real_aliexpress_bot.py`Monitoring:   Flower, Sentry

- **Función**: Scraping real de productos de AliExpressNotifications: Telegram Bot API, Discord Webhooks

- **Estrategias**: Múltiples métodos de búsqueda con fallbackTesting:      pytest-django, APITestCase

- **Anti-detección**: Headers realistas, rotación de agentesDeploy:       Docker + Docker Compose

- **Filtrado**: Precio, envío, rating en tiempo real```



### 2. API REST### Diagrama de Arquitectura

**Archivo**: `products/real_views.py`

- **Endpoints**:```

  - `POST /real-filter/` - Búsqueda de productos┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐

  - `GET /real-filter/info/` - Información del sistema│   Web Frontend  │    │  Notifications  │    │   Async Tasks   │

  - `GET /real-filter/quick-test/` - Test rápido│                 │    │                 │    │                 │

  - `GET /real-filter-ui/` - Interfaz web│ - Dashboard     │    │ - Telegram Bot  │    │ - Celery Worker │

│ - Analytics     │    │ - Discord       │    │ - Celery Beat   │

### 3. Interfaz Web│ - Bootstrap UI  │    │   Webhooks      │    │ - Redis Queue   │

**Archivo**: `templates/real_filter.html`└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘

- **Framework**: Bootstrap 5          │                      │                      │

- **Características**: Responsive, AJAX, indicadores en tiempo real          ▼                      ▼                      ▼

- **Funcionalidad**: Formulario de búsqueda, filtros, resultados┌─────────────────────────────────────────────────────────────────┐

│                    Django Application                           │

### 4. Sistema de Configuración│                                                                 │

**Archivo**: `dropship_bot/settings.py`│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │

- **Base de datos**: SQLite por defecto, escalable a PostgreSQL│  │   Models    │  │    Views    │  │ Serializers │             │

- **Templates**: Configurado para carpeta templates/│  │             │  │             │  │             │             │

- **Seguridad**: Headers SSL, CORS habilitado│  │ - Product   │  │ - ViewSets  │  │ - DRF       │             │

- **Extensions**: django-extensions para HTTPS│  │ - ScrapeJob │  │ - Dashboard │  │ - Jobs      │             │

│  └─────────────┘  └─────────────┘  └─────────────┘             │

## 📊 Modelos de Datos│                                                                 │

│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │

### Product Model│  │  Services   │  │   Filters   │  │   Scrapers  │             │

```python│  │             │  │             │  │             │             │

class Product(models.Model):│  │ - Managers  │  │ - Query     │  │ - Advanced  │             │

    title = CharField(max_length=500)│  │ - Notifs    │  │ - List      │  │ - Mock      │             │

    price = DecimalField(max_digits=10, decimal_places=2)│  │ - Tasks     │  │ - Async     │  │ - Real      │             │

    currency = CharField(max_length=3, default='USD')│  └─────────────┘  └─────────────┘  └─────────────┘             │

    url = URLField(unique=True)  # Previene duplicados└─────────────────────────────────────────────────────────────────┘

    image_url = URLField(blank=True)                                    │

    rating = DecimalField(max_digits=3, decimal_places=2)                                    ▼

    rating_count = IntegerField(default=0)              ┌─────────────────┐        ┌─────────────────┐

    shipping_days = IntegerField(default=0)              │   PostgreSQL    │        │      Redis      │

    category = CharField(max_length=100)              │                 │        │                 │

    description = TextField(blank=True)              │ - Products      │        │ - Cache         │

    created_at = DateTimeField(auto_now_add=True)              │ - ScrapeJobs    │        │ - Queue         │

    updated_at = DateTimeField(auto_now=True)              │ - Users         │        │ - Sessions      │

```              └─────────────────┘        └─────────────────┘

```

## 🔄 Flujo de Datos

---

### Búsqueda de Productos

1. **Entrada**: Usuario envía solicitud vía API o interfaz web## 🚀 Instalación y Configuración {#instalacion}

2. **Validación**: Validación de parámetros (keywords, precio, etc.)

3. **Scraping**: Bot real intenta scraping de AliExpress### Requisitos del Sistema

4. **Fallback**: Si falla, genera productos realistas

5. **Filtrado**: Aplica filtros de precio, envío, rating```bash

6. **Respuesta**: JSON con productos encontrados# Requisitos mínimos

- Python 3.13+

### Estructura de Respuesta API- 4GB RAM

```json- 2GB espacio en disco

{- SO: Windows/Linux/macOS

  "products": [

    {# Requisitos de producción

      "title": "Wireless Gaming Mouse",- Python 3.13+

      "price": "$29.99",- 8GB RAM

      "currency": "USD",- 20GB espacio en disco

      "url": "https://aliexpress.com/...",- PostgreSQL 16+

      "image_url": "https://...",- Redis 7+

      "rating": 4.5,- Docker + Docker Compose

      "rating_count": 1250,```

      "shipping_days": 15,

      "category": "Electronics"### Instalación Paso a Paso

    }

  ],#### 1. Clonar y Configurar Entorno

  "real_products": true,

  "source": "aliexpress_real",```bash

  "total_found": 5,git clone [tu-repo]

  "filters_applied": {cd Dropshiping

    "min_price": 15,

    "max_price": 45,# Crear entorno virtual

    "max_shipping_days": 30python -m venv .venv

  }

}# Activar entorno

```# Windows

.venv\Scripts\activate

## 🛡️ Seguridad y HTTPS# Linux/Mac

source .venv/bin/activate

### Configuración SSL```

- **Certificados**: Autofirmados en `certs/`

- **Servidor**: django-extensions + Werkzeug#### 2. Instalar Dependencias

- **Puerto**: 8443 para HTTPS

- **Headers**: Configurados para seguridad```bash

pip install -r requirements.txt

### Anti-detección Bot```

- **User Agents**: Rotación de navegadores realistas

- **Headers**: Accept, Accept-Language, Accept-Encoding**requirements.txt completo:**

- **Delays**: Esperas aleatorias entre requests```

- **Fallback**: Sistema robusto ante bloqueosDjango==5.2.6

djangorestframework==3.16.1

## 🔨 Comandos de Desarrollodjango-crontab==0.7.1

django-filter==25.1

### Servidor de Desarrollorequests==2.32.5

```bashpython-telegram-bot==22.5

# HTTP (desarrollo)

python manage.py runserver 127.0.0.1:8000# Para desarrollo

coverage==7.6.9

# HTTPS (producción-like)pytest-django==4.8.0

python manage.py runserver_plus --cert-file certs/cert.pem --key-file certs/key.pem 127.0.0.1:8443```

```

#### 3. Variables de Entorno

### Tests

```bashCrear `.env` (opcional):

# Test principal del bot real```bash

python test_bot_real.py# Django

SECRET_KEY=tu-secret-key-super-segura-aqui

# Test de APIDEBUG=True

python test_api_final.pyALLOWED_HOSTS=localhost,127.0.0.1



# Demo completo# Database (opcional - por defecto usa SQLite)

python demo_final_real.pyDATABASE_URL=postgresql://user:pass@localhost:5432/dropship_db

```

# Telegram

## 🚀 DespliegueTELEGRAM_BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ

TELEGRAM_CHAT_ID=123456789

### Configuración de Producción

1. **Variables de entorno**: Configurar en `.env`# Discord

2. **Base de datos**: Migrar a PostgreSQLDISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/123/abc

3. **Servidor web**: Nginx + Gunicorn

4. **SSL**: Certificados válidos# Logging

5. **Monitoreo**: Logs y métricasLOG_LEVEL=INFO

LOG_FILE=dropship_bot.log

### Variables de Entorno```

```bash

DEBUG=False#### 4. Configuración de Base de Datos

DATABASE_URL=postgresql://user:pass@host:port/db

SECRET_KEY=your-secret-key```bash

ALLOWED_HOSTS=your-domain.com# Aplicar migraciones

```python manage.py migrate



## 🧪 Testing# Crear superusuario (opcional)

python manage.py createsuperuser

### Archivos de Test```

- `test_bot_real.py` - Test completo del bot real

- `test_api_final.py` - Test de endpoints API#### 5. Verificar Instalación

- `test_real_scraper.py` - Test del scraper

- `demo_final_real.py` - Demostración funcional```bash

# Ejecutar tests

### Cobertura de Testspython manage.py test products

- ✅ Scraping real de AliExpress

- ✅ Sistema de fallback# Iniciar servidor

- ✅ Endpoints APIpython manage.py runserver

- ✅ Filtros de productos

- ✅ Validación de datos# Probar API

- ✅ Manejo de errorescurl http://localhost:8000/health/

```

## 📈 Escalabilidad

---

### Optimizaciones Futuras

- **Cache**: Redis para resultados frecuentes## 📁 Estructura del Código {#estructura}

- **Queue**: Celery para scraping asíncrono

- **CDN**: Para imágenes de productos### Estructura de Directorios

- **Sharding**: Base de datos distribuida

- **Rate Limiting**: Control de requests por API```

dropship_bot/

### Monitoreo├── dropship_bot/               # Configuración principal

- **Logs**: Estructurados en `logs/`│   ├── __init__.py

- **Métricas**: Performance del scraping│   ├── settings.py            # Configuraciones Django

- **Alertas**: Fallos del bot│   ├── urls.py               # URLs principales

- **Health Checks**: Endpoints de estado│   ├── wsgi.py               # WSGI application

│   └── asgi.py               # ASGI application (futuro)

## 🔧 Troubleshooting│

├── products/                  # App principal

### Problemas Comunes│   ├── __init__.py

1. **Error 404**: Verificar configuración de URLs│   ├── apps.py               # Configuración de la app

2. **SSL Issues**: Regenerar certificados│   ├── models.py             # Modelo Product

3. **Scraping Fails**: AliExpress puede bloquear IPs│   ├── views.py              # ViewSets DRF

4. **Imports**: Verificar estructura de directorios│   ├── serializers.py        # Serializers DRF

│   ├── urls.py               # URLs de la app

### Logs Importantes│   ├── admin.py              # Admin interface

- `dropship_bot.log` - Log general de Django│   ├── signals.py            # Django signals

- `logs/monitor.log` - Log de monitoreo│   ├── cron.py               # Tareas programadas

- Console output - Errores de scraping en tiempo real│   ├── tests.py              # Tests unitarios

│   │

---│   ├── services/             # Servicios de negocio

│   │   ├── __init__.py

**Última actualización**: October 2025  │   │   ├── scraper.py        # Sistema de scraping

**Versión Django**: 5.2.6  │   │   ├── filters.py        # Sistema de filtros

**Python**: 3.8+│   │   ├── notifications.py  # Sistema de notificaciones
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

---

## 🔄 Scraping Asíncrono {#async-scraping}

### Modelo ScrapeJob

El sistema implementa un tracking completo de trabajos de scraping usando el modelo `ScrapeJob`:

```python
class ScrapeJob(models.Model):
    """Modelo para trackear trabajos de scraping asíncronos"""
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('running', 'Ejecutándose'),
        ('success', 'Completado'),
        ('failed', 'Fallido'),
        ('revoked', 'Cancelado'),
    ]
    
    task_id = models.CharField(max_length=255, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    query = models.CharField(max_length=500, blank=True)
    source = models.CharField(max_length=100, default='aliexpress')
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    products_found = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    
    def mark_started(self):
        """Marcar job como iniciado"""
        self.status = 'running'
        self.started_at = timezone.now()
        self.save()
    
    def mark_success(self, products_count=0):
        """Marcar job como exitoso"""
        self.status = 'success'
        self.completed_at = timezone.now()
        self.products_found = products_count
        self.save()
    
    def mark_failure(self, error_msg):
        """Marcar job como fallido"""
        self.status = 'failed'
        self.completed_at = timezone.now()
        self.error_message = error_msg
        self.save()
```

### Endpoints de Scraping Asíncrono

```python
# Lanzar scraping asíncrono
POST /api/async-scrape/launch/
{
    "query": "smartphone",
    "source": "aliexpress",
    "max_products": 50
}

# Respuesta
{
    "task_id": "abc123-def456",
    "status": "pending",
    "message": "Scraping iniciado"
}

# Consultar estado
GET /api/async-scrape/status/{task_id}/

# Listar todos los jobs
GET /api/scrape-jobs/

# Cancelar job
POST /api/scrape-jobs/{id}/cancel/
```

### Celery Tasks

```python
@shared_task(bind=True)
def scrape_products_async(self, query, source='aliexpress', max_products=50):
    """Tarea asíncrona para scraping de productos"""
    job = ScrapeJob.objects.get(task_id=self.request.id)
    
    try:
        job.mark_started()
        
        # Ejecutar scraping
        scraper = AdvancedScraper()
        products = scraper.scrape_products(
            query=query,
            source=source,
            max_products=max_products
        )
        
        # Procesar resultados
        created_count = 0
        for product_data in products:
            product, created = Product.objects.get_or_create(
                url=product_data['url'],
                defaults=product_data
            )
            if created:
                created_count += 1
        
        job.mark_success(created_count)
        
        # Notificaciones automáticas
        send_notification(f"✅ Scraping completado: {created_count} productos nuevos")
        
        return {
            'status': 'success',
            'products_found': len(products),
            'products_created': created_count
        }
        
    except Exception as e:
        job.mark_failure(str(e))
        send_notification(f"❌ Error en scraping: {str(e)}")
        raise
```

---

## 📊 Dashboard y Analytics {#dashboard}

### Interfaz Web del Dashboard

El sistema incluye una interfaz web completa desarrollada con Django Templates, Bootstrap 5 y Chart.js:

#### URLs del Dashboard

```python
# Dashboard principal
GET /products/dashboard/

# Analytics avanzados  
GET /products/analytics/

# API para datos del dashboard
GET /api/dashboard/stats/
GET /api/analytics/scraping/
GET /api/analytics/trends/
```

#### Estructura del Dashboard

```html
<!-- templates/products/dashboard.html -->
{% extends 'products/base.html' %}

{% block content %}
<!-- Estadísticas principales -->
<div id="mainStats" class="stats-grid">
    <!-- KPIs dinámicos -->
</div>

<!-- Gráficos interactivos -->
<div class="row">
    <!-- Productos por día -->
    <canvas id="dailyChart"></canvas>
    
    <!-- Distribución por categorías -->
    <canvas id="categoryChart"></canvas>
    
    <!-- Productos por hora -->
    <canvas id="hourlyChart"></canvas>
</div>

<!-- Tablas de top productos -->
<div class="top-products-section">
    <!-- Mejor valorados, más baratos, más caros -->
</div>

<!-- Estado del sistema -->
<div class="system-status">
    <!-- Conectividad DB, Redis, último scraping -->
</div>
{% endblock %}
```

#### JavaScript para Charts

```javascript
// Cargar datos del dashboard
async function loadDashboardData() {
    const response = await fetch('/api/dashboard/stats/');
    const data = await response.json();
    
    renderMainStats(data.summary);
    renderTopProducts(data.top_lists);
    renderDailyChart(data.charts.daily_products);
    renderCategoryChart(data.charts.category_distribution);
}

// Renderizar gráfico diario
function renderDailyChart(data) {
    const ctx = document.getElementById('dailyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(item => item.date),
            datasets: [{
                label: 'Productos por Día',
                data: data.map(item => item.count),
                borderColor: '#36A2EB',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false
        }
    });
}

// Auto-refresh cada 30 segundos
setInterval(loadDashboardData, 30000);
```

### Analytics API Endpoints

```python
class DashboardStatsView(APIView):
    """Estadísticas completas para el dashboard"""
    
    def get(self, request):
        now = timezone.now()
        today = now.date()
        
        # Estadísticas básicas
        total_products = Product.objects.count()
        products_today = Product.objects.filter(created_at__date=today).count()
        
        # Estadísticas de precios
        price_stats = Product.objects.aggregate(
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        )
        
        # Productos top
        top_rated = Product.objects.order_by('-rating')[:10]
        cheapest = Product.objects.order_by('price')[:10]
        most_expensive = Product.objects.order_by('-price')[:10]
        
        # Gráficos
        daily_products = self.get_daily_products()
        category_distribution = self.get_category_distribution()
        
        return Response({
            'summary': {
                'total_products': total_products,
                'products_today': products_today,
                'average_price': price_stats['avg_price'],
                'min_price': price_stats['min_price'],
                'max_price': price_stats['max_price'],
            },
            'top_lists': {
                'top_rated': ProductListSerializer(top_rated, many=True).data,
                'cheapest': ProductListSerializer(cheapest, many=True).data,
                'most_expensive': ProductListSerializer(most_expensive, many=True).data,
            },
            'charts': {
                'daily_products': daily_products,
                'category_distribution': category_distribution,
            }
        })
```

---

## 🔔 Sistema de Notificaciones {#notifications}

### Filtros de Notificaciones Avanzados

```python
class NotificationFilter:
    """Sistema avanzado de filtros para notificaciones"""
    
    def __init__(self, config):
        self.price_range = config.get('price_range', {})
        self.keywords = config.get('keywords', [])
        self.categories = config.get('categories', [])
        self.rating_threshold = config.get('min_rating', 0)
        self.platforms = config.get('platforms', [])
    
    def should_notify(self, product):
        """Determinar si un producto debe generar notificación"""
        
        # Filtro de precio
        if self.price_range:
            min_price = self.price_range.get('min', 0)
            max_price = self.price_range.get('max', float('inf'))
            if not (min_price <= product.price <= max_price):
                return False
        
        # Filtro de keywords
        if self.keywords:
            title_lower = product.title.lower()
            if not any(keyword.lower() in title_lower for keyword in self.keywords):
                return False
        
        # Filtro de rating
        if product.rating < self.rating_threshold:
            return False
        
        return True

# Configuración de filtros
NOTIFICATION_FILTERS = {
    'telegram': NotificationFilter({
        'price_range': {'min': 10, 'max': 100},
        'keywords': ['smartphone', 'laptop', 'gaming'],
        'min_rating': 4.0,
        'platforms': ['aliexpress']
    }),
    'discord': NotificationFilter({
        'price_range': {'min': 50, 'max': 500},
        'categories': ['Electronics', 'Computers'],
        'min_rating': 4.5
    })
}
```

### Templates de Notificaciones

```python
class NotificationTemplates:
    """Templates para diferentes tipos de notificaciones"""
    
    PRODUCT_FOUND = """
🔍 **Nuevo Producto Encontrado**

📱 **{title}**
💰 Precio: ${price}
⭐ Rating: {rating}/5
🚚 Envío: {shipping_time} días
🏪 Plataforma: {source_platform}
🔗 [Ver Producto]({url})

#{category} #{source_platform}
    """
    
    SCRAPING_COMPLETE = """
✅ **Scraping Completado**

📊 **Estadísticas:**
- Productos encontrados: {products_found}
- Productos nuevos: {products_created}
- Tiempo total: {duration}
- Query: "{query}"

🔗 [Ver Dashboard](http://localhost:8000/products/dashboard/)
    """
    
    SCRAPING_ERROR = """
❌ **Error en Scraping**

⚠️ **Detalles:**
- Query: "{query}"
- Error: {error_message}
- Tiempo: {timestamp}

🔧 [Ver Logs](http://localhost:8000/admin/)
    """
    
    @staticmethod
    def format_product_notification(product, template_type='PRODUCT_FOUND'):
        """Formatear notificación de producto"""
        template = getattr(NotificationTemplates, template_type)
        return template.format(
            title=product.title,
            price=product.price,
            rating=product.rating,
            shipping_time=product.shipping_time,
            source_platform=product.source_platform,
            url=product.url,
            category=product.category
        )
```

### Comandos de Gestión

```bash
# Gestionar filtros de notificaciones
python manage.py manage_notifications --filters --list
python manage.py manage_notifications --filters --add \
    --name "high_value" \
    --min_price 100 \
    --max_price 1000 \
    --min_rating 4.5

# Gestionar plantillas
python manage.py manage_notifications --templates --list
python manage.py manage_notifications --templates --test \
    --type PRODUCT_FOUND \
    --product_id 123

# Estadísticas del sistema
python manage.py manage_notifications --stats
```

---

## 🧪 Testing Automático {#testing}

### Tests de ScrapeJob

```python
# products/test_scrape_jobs.py
class ScrapeJobAPITestCase(APITestCase):
    """Tests para endpoints de ScrapeJob"""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_launch_async_scrape(self):
        """Test lanzar scraping asíncrono"""
        url = reverse('async-scrape-launch')
        data = {
            'query': 'test product',
            'source': 'aliexpress',
            'max_products': 10
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['status'], 'pending')
        
        # Verificar que se creó el ScrapeJob
        job = ScrapeJob.objects.get(task_id=response.data['task_id'])
        self.assertEqual(job.query, 'test product')
        self.assertEqual(job.status, 'pending')
    
    def test_scrape_job_status(self):
        """Test consultar estado de job"""
        job = ScrapeJob.objects.create(
            task_id='test-task-123',
            query='test',
            status='running'
        )
        
        url = reverse('async-scrape-status', kwargs={'task_id': job.task_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'running')
        self.assertEqual(response.data['query'], 'test')
    
    def test_cancel_scrape_job(self):
        """Test cancelar job de scraping"""
        job = ScrapeJob.objects.create(
            task_id='test-task-456',
            query='test',
            status='pending'
        )
        
        url = reverse('scrapejob-cancel', kwargs={'pk': job.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que el job se marcó como cancelado
        job.refresh_from_db()
        self.assertEqual(job.status, 'revoked')
    
    @patch('products.tasks.scrape_products_async.delay')
    def test_async_scrape_integration(self, mock_task):
        """Test integración completa de scraping asíncrono"""
        mock_task.return_value.id = 'test-task-789'
        
        url = reverse('async-scrape-launch')
        data = {'query': 'integration test'}
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_task.assert_called_once()
        
        # Verificar argumentos de la tarea
        args, kwargs = mock_task.call_args
        self.assertEqual(kwargs['query'], 'integration test')
```

### Tests de Dashboard

```python
class DashboardAPITestCase(APITestCase):
    """Tests para endpoints del dashboard"""
    
    def setUp(self):
        # Crear datos de prueba
        self.products = [
            Product.objects.create(
                title=f"Product {i}",
                price=Decimal(f"{10 + i}.99"),
                rating=4.0 + (i * 0.1),
                category="Electronics",
                source_platform="aliexpress"
            )
            for i in range(10)
        ]
    
    def test_dashboard_stats(self):
        """Test estadísticas del dashboard"""
        url = reverse('dashboard-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar estructura de respuesta
        self.assertIn('summary', response.data)
        self.assertIn('top_lists', response.data)
        self.assertIn('charts', response.data)
        
        # Verificar estadísticas
        summary = response.data['summary']
        self.assertEqual(summary['total_products'], 10)
        self.assertIsNotNone(summary['average_price'])
    
    def test_analytics_endpoints(self):
        """Test endpoints de analytics"""
        urls = [
            reverse('scraping-analytics'),
            reverse('trend-analysis'),
        ]
        
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### Ejecutar Tests

```bash
# Tests completos
python manage.py test

# Tests específicos
python manage.py test products.test_scrape_jobs
python manage.py test products.test_scrape_jobs.ScrapeJobAPITestCase.test_launch_async_scrape

# Tests con cobertura
coverage run manage.py test
coverage report
coverage html

# Tests en paralelo
python manage.py test --parallel
```

---

## 🐳 Deployment con Docker {#deployment}
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

### Deployment de Producción

#### 1. Configuración de Variables de Entorno

```bash
# .env.production
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com

# Base de datos
DATABASE_NAME=dropship_db
DATABASE_USER=dropship_user
DATABASE_PASSWORD=dropship_pass_2025
DATABASE_HOST=db
DATABASE_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Admin
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@localhost

# Notificaciones
TELEGRAM_BOT_TOKEN=tu-bot-token
TELEGRAM_CHAT_ID=tu-chat-id
DISCORD_WEBHOOK_URL=tu-webhook-url

# Monitoreo
SENTRY_DSN=
FLOWER_BASIC_AUTH=admin:admin
```

#### 2. Docker Compose de Producción

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  app:
    build:
      context: .
      dockerfile: Dockerfile.production
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1}
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@db:5432/${DATABASE_NAME}
      - DATABASE_NAME=${DATABASE_NAME}
      - DATABASE_USER=${DATABASE_USER}
      - DATABASE_PASSWORD=${DATABASE_PASSWORD}
      - DATABASE_HOST=db
      - DATABASE_PORT=5432
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_ENV=production
      - DJANGO_SUPERUSER_USERNAME=${ADMIN_USERNAME:-admin}
      - DJANGO_SUPERUSER_PASSWORD=${ADMIN_PASSWORD:-admin123}
      - DJANGO_SUPERUSER_EMAIL=${ADMIN_EMAIL:-admin@localhost}
    command: ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "dropship_bot.wsgi:application"]
    restart: unless-stopped
    volumes:
      - media_data:/app/media
      - static_data:/app/static
      - backup_data:/app/backups
      - log_data:/app/logs
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  db:
    image: postgres:16-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - backup_data:/backups
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DATABASE_USER}"]
      interval: 30s
      timeout: 10s
      retries: 5

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    command: ["redis-server", "--appendonly", "yes"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5

  celery-worker:
    profiles: ["celery"]
    build:
      context: .
      dockerfile: Dockerfile.production
    command: ["celery", "-A", "dropship_bot", "worker", "--loglevel=INFO", "-Q", "default"]
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1}
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@db:5432/${DATABASE_NAME}
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_ENV=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      app:
        condition: service_started
    restart: unless-stopped
    volumes:
      - media_data:/app/media
      - static_data:/app/static

  celery-beat:
    profiles: ["celery"]
    build:
      context: .
      dockerfile: Dockerfile.production
    command: ["celery", "-A", "dropship_bot", "beat", "--loglevel=INFO"]
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - ALLOWED_HOSTS=${ALLOWED_HOSTS:-localhost,127.0.0.1}
      - DATABASE_URL=postgresql://${DATABASE_USER}:${DATABASE_PASSWORD}@db:5432/${DATABASE_NAME}
      - REDIS_URL=redis://redis:6379/0
      - DJANGO_ENV=production
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      app:
        condition: service_started
    restart: unless-stopped
    volumes:
      - media_data:/app/media
      - static_data:/app/static

  flower:
    profiles: ["celery", "monitoring"]
    image: mher/flower:2.0
    environment:
      - FLOWER_PORT=5555
      - CELERY_BROKER_URL=redis://redis:6379/0
      - FLOWER_BASIC_AUTH=${FLOWER_BASIC_AUTH:-admin:admin}
    command: ["flower", "--url_prefix=flower", "--port=5555", "--broker=redis://redis:6379/0"]
    ports:
      - "5555:5555"
    depends_on:
      redis:
        condition: service_healthy
    restart: unless-stopped

  nginx:
    profiles: ["nginx"]
    image: nginx:1.27-alpine
    depends_on:
      app:
        condition: service_started
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - static_data:/app/static:ro
      - media_data:/app/media:ro
      - ./nginx.conf:/etc/nginx/conf.d/default.conf:ro
      - certs_data:/etc/ssl/certs:ro
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped

volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  media_data:
    driver: local
  static_data:
    driver: local
  log_data:
    driver: local
  backup_data:
    driver: local
  certs_data:
    driver: local

networks:
  default:
    driver: bridge
```

#### 3. Dockerfile de Producción

```dockerfile
# Dockerfile.production
# Multi-stage build para optimizar imagen final
FROM python:3.13-slim-bullseye as base

# Stage 1: Builder
FROM base as builder

# Instalar dependencias del sistema para building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Crear virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Actualizar pip y instalar wheel
RUN pip install --upgrade pip wheel setuptools

# Instalar dependencias Python
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Stage 2: Production
FROM base as production

# Instalar dependencias runtime
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Copiar virtual environment del builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Crear usuario no-root
RUN groupadd -r appuser && \
    useradd -r -g appuser -d /app -s /bin/bash appuser

# Crear directorios de la aplicación
RUN mkdir -p /app /app/logs /app/media /app/static /app/backups && \
    chown -R appuser:appuser /app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar código de la aplicación
COPY --chown=appuser:appuser . .

# Hacer ejecutables los scripts
RUN chmod +x manage.py && \
    chmod +x deploy_production.py && \
    chmod +x monitor_production.py && \
    chmod +x backup_production.py

# Copiar y hacer ejecutable el entrypoint
COPY --chown=appuser:appuser docker-entrypoint.sh /app/
RUN chmod +x docker-entrypoint.sh

# Cambiar a usuario no-root
USER appuser

# Exponer puerto
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Entrypoint
ENTRYPOINT ["/app/docker-entrypoint.sh"]
```

#### 4. Script de Entrypoint

```bash
#!/bin/bash
# docker-entrypoint.sh

🚀 Docker Entry Point - Dropshipping Assistant
Script de entrada para contenedor de producción

echo "🚀 Iniciando Dropshipping Assistant..."
echo "[INFO] === INICIALIZANDO APLICACIÓN ==="

echo "[INFO] Verificando variables de entorno..."
if [ -z "$SECRET_KEY" ]; then
    echo "[ERROR] SECRET_KEY no está configurada"
    exit 1
fi
echo "[INFO] Variables de entorno verificadas ✅"

echo "[INFO] Esperando a que la base de datos esté disponible..."
until python manage.py dbshell --command="SELECT 1;" > /dev/null 2>&1; do
    echo "[WARNING] Base de datos no disponible, esperando 5 segundos..."
    sleep 5
done
echo "[INFO] Base de datos disponible ✅"

echo "[INFO] Ejecutando migraciones..."
python manage.py migrate --noinput
echo "[INFO] Migraciones completadas ✅"

echo "[INFO] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear
echo "[INFO] Archivos estáticos recolectados ✅"

echo "[INFO] Creando superusuario si no existe..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@localhost', 'admin123')
    print('Superusuario creado')
else:
    print('Superusuario ya existe')
"

echo "[INFO] === INICIANDO SERVICIOS ==="
echo "[INFO] Aplicación lista para recibir tráfico ✅"

# Ejecutar comando pasado como argumento o comando por defecto
exec "$@"
```

#### 5. Comandos de Deployment

```bash
# 1. Preparar archivos de configuración
cp .env.production .env

# 2. Construir imágenes
docker compose -f docker-compose.prod.yml build --no-cache

# 3. Levantar servicios principales
docker compose -f docker-compose.prod.yml up -d

# 4. Levantar Celery workers (opcional)
docker compose -f docker-compose.prod.yml --profile celery up -d

# 5. Levantar monitoreo (opcional)
docker compose -f docker-compose.prod.yml --profile monitoring up -d

# 6. Levantar nginx (opcional)
docker compose -f docker-compose.prod.yml --profile nginx up -d

# 7. Verificar estado de servicios
docker compose -f docker-compose.prod.yml ps

# 8. Ver logs
docker compose -f docker-compose.prod.yml logs -f app
```

#### 6. URLs de Producción

```bash
# Aplicación principal
http://localhost:8000

# Dashboard
http://localhost:8000/products/dashboard/

# Analytics
http://localhost:8000/products/analytics/

# API REST
http://localhost:8000/api/products/

# Admin Django
http://localhost:8000/admin/

# API Documentation
http://localhost:8000/api/docs/

# Flower (monitoreo Celery)
http://localhost:5555

# Health Check
http://localhost:8000/api/health/status/
```

#### 7. Configuración de Nginx (Opcional)

```nginx
# nginx.conf
server {
    listen 80;
    server_name localhost;

    location / {
        proxy_pass http://app:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /app/media/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /flower/ {
        proxy_pass http://flower:5555;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
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

## 📊 Monitoreo y Logs {#monitoring}

### Flower - Monitoreo de Celery

Flower proporciona una interfaz web para monitorear workers de Celery:

```bash
# Acceder a Flower
http://localhost:5555

# Autenticación básica (configurada en .env)
Usuario: admin
Contraseña: admin

# Ver workers activos
http://localhost:5555/workers

# Ver tareas en tiempo real
http://localhost:5555/tasks

# Estadísticas de performance
http://localhost:5555/monitor
```

### Logs del Sistema

```bash
# Logs de la aplicación principal
docker compose logs -f app

# Logs de Celery worker
docker compose logs -f celery-worker

# Logs de Celery beat (scheduler)
docker compose logs -f celery-beat

# Logs de base de datos
docker compose logs -f db

# Logs de Redis
docker compose logs -f redis

# Logs combinados
docker compose logs -f

# Logs con timestamp
docker compose logs -f -t

# Últimos N logs
docker compose logs --tail 100 app
```

### Archivos de Log

```bash
# Ubicación de logs dentro del contenedor
/app/logs/
├── django.log          # Logs de Django
├── celery.log          # Logs de Celery
├── scraper.log         # Logs de scraping
├── notifications.log   # Logs de notificaciones
└── error.log           # Logs de errores

# Configuración de logging en settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {name} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

### Health Checks

```bash
# Health check de la aplicación
curl http://localhost:8000/api/health/status/

# Respuesta típica
{
    "status": "healthy",
    "database": "ok",
    "redis": "ok",
    "products_count": 1250,
    "last_scrape": "2025-10-06T10:30:00Z",
    "celery_workers": 2,
    "system_info": {
        "django_version": "5.2.6",
        "python_version": "3.13.0",
        "environment": "production"
    }
}

# Health checks de Docker
docker compose ps  # Ver estado de contenedores
```

### Métricas y Estadísticas

```python
# Endpoint de métricas del sistema
GET /api/dashboard/stats/

# Métricas de Celery
GET /api/celery/stats/

# Ejemplo de métricas
{
    "products": {
        "total": 1250,
        "today": 45,
        "this_week": 320,
        "average_price": 35.67
    },
    "scraping": {
        "jobs_pending": 2,
        "jobs_running": 1,
        "jobs_completed": 156,
        "jobs_failed": 3,
        "success_rate": 98.1
    },
    "system": {
        "uptime": "2 days, 14:32:10",
        "memory_usage": "256MB",
        "cpu_usage": "12%",
        "disk_usage": "2.1GB"
    }
}
```

### Alertas y Notificaciones

```python
# Configuración de alertas automáticas
MONITORING_ALERTS = {
    'high_error_rate': {
        'threshold': 5,  # 5% de error
        'window': 300,   # 5 minutos
        'channels': ['telegram', 'discord']
    },
    'low_disk_space': {
        'threshold': 90,  # 90% uso
        'channels': ['telegram']
    },
    'celery_workers_down': {
        'threshold': 0,   # Sin workers
        'channels': ['telegram', 'discord']
    }
}

# Comando para verificar alertas
python manage.py check_system_alerts
```

---

## 🔧 Troubleshooting {#troubleshooting}

### Problemas Comunes

#### 1. Error de Conectividad a Base de Datos

```bash
# Síntoma
django.db.utils.OperationalError: could not connect to server

# Diagnóstico
docker compose ps  # Verificar estado de DB
docker compose logs db  # Ver logs de PostgreSQL

# Solución
docker compose restart db
docker compose restart app
```

#### 2. Error de Redis/Celery

```bash
# Síntoma
celery.exceptions.WorkerLostError

# Diagnóstico
docker compose logs redis
docker compose logs celery-worker

# Solución
docker compose restart redis
docker compose restart celery-worker celery-beat
```

#### 3. Error de Permisos

```bash
# Síntoma
PermissionError: [Errno 13] Permission denied

# Solución
docker compose exec --user root app chown -R appuser:appuser /app/logs
docker compose restart app
```

#### 4. Error de Variables de Entorno

```bash
# Síntoma
KeyError: 'SECRET_KEY'

# Diagnóstico
docker compose exec app env | grep SECRET_KEY

# Solución
# Verificar .env y reiniciar
cp .env.production .env
docker compose down
docker compose up -d
```

#### 5. Error de Migraciones

```bash
# Síntoma
django.db.migrations.exceptions.InconsistentMigrationHistory

# Solución
docker compose exec app python manage.py migrate --fake-initial
docker compose exec app python manage.py migrate
```

#### 6. Error de psycopg2 con Python 3.13

```bash
# Síntoma
ImportError: undefined symbol: _PyInterpreterState_Get

# Solución
docker compose exec --user root app pip install psycopg2-binary --force-reinstall
docker compose restart app
```

### Comandos de Diagnóstico

```bash
# Estado general del sistema
docker compose ps
docker stats

# Uso de recursos
docker compose exec app df -h  # Espacio en disco
docker compose exec app free -h  # Memoria
docker compose exec app top  # Procesos

# Conectividad de red
docker compose exec app ping db
docker compose exec app ping redis

# Verificar configuración
docker compose config  # Validar docker-compose.yml
docker compose exec app python manage.py check  # Verificar Django

# Limpiar sistema
docker system prune -a  # Limpiar imágenes no usadas
docker volume prune  # Limpiar volúmenes no usados
```

### Backup y Restauración

```bash
# Backup de base de datos
docker compose exec db pg_dump -U dropship_user dropship_db > backup.sql

# Restaurar base de datos
docker compose exec -T db psql -U dropship_user dropship_db < backup.sql

# Backup de volúmenes
docker run --rm -v dropshiping_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres_backup.tar.gz -C /data .

# Script de backup automático (se ejecuta desde el contenedor)
python backup_production.py
```

### Performance Tuning

```bash
# Optimizar PostgreSQL
# En docker-compose.prod.yml, agregar a service db:
environment:
  - POSTGRES_SHARED_PRELOAD_LIBRARIES=pg_stat_statements
  - POSTGRES_MAX_CONNECTIONS=100
  - POSTGRES_SHARED_BUFFERS=256MB

# Optimizar Celery
# Ajustar número de workers
docker compose -f docker-compose.prod.yml scale celery-worker=4

# Monitorear performance
docker compose exec app python manage.py shell
>>> from django.db import connection
>>> print(connection.queries)  # Ver queries SQL
```

### Logs de Debugging

```bash
# Habilitar debug logging
docker compose exec app python manage.py shell -c "
import logging
logging.getLogger('products').setLevel(logging.DEBUG)
"

# Ver logs en tiempo real con filtros
docker compose logs -f app 2>&1 | grep ERROR
docker compose logs -f celery-worker 2>&1 | grep -i "scraping"

# Exportar logs para análisis
docker compose logs app > app_logs.txt
```

---

## 🤝 Contribución y Mantenimiento

### Versionado

```bash
# Versión actual del sistema
Version: 2.0.0
Release Date: Octubre 2025
Python: 3.13+
Django: 5.2.6

# Changelog
v2.0.0 - Octubre 2025
- ✅ Scraping asíncrono con Celery
- ✅ Dashboard web con Bootstrap 5
- ✅ Sistema de notificaciones avanzado
- ✅ Docker Compose de producción
- ✅ Tests automáticos
- ✅ Monitoreo con Flower

v1.0.0 - Septiembre 2025
- ✅ Scraping básico
- ✅ API REST
- ✅ Filtros de productos
- ✅ Notificaciones básicas
```

### Actualización del Sistema

```bash
# 1. Backup antes de actualizar
python backup_production.py

# 2. Detener servicios
docker compose down

# 3. Pull nuevos cambios
git pull origin main

# 4. Reconstruir imágenes
docker compose build --no-cache

# 5. Actualizar base de datos
docker compose up -d db redis
docker compose run --rm app python manage.py migrate

# 6. Levantar servicios
docker compose -f docker-compose.prod.yml --profile celery --profile monitoring up -d

# 7. Verificar estado
docker compose ps
curl http://localhost:8000/api/health/status/
```

**Documentación actualizada: Octubre 2025**
**Versión del sistema: 2.0.0**