# Dropship Bot - Asistente de Dropshipping

Un asistente modular de dropshipping construido con Django que proporciona scraping automatizado, filtrado inteligente, persistencia de datos y notificaciones en tiempo real.

## 🚀 Características

- **Scraping Modular**: Sistema extensible para scrapear productos de múltiples plataformas
- **Filtrado Inteligente**: Filtros avanzados por precio, categoría, tiempo de envío, calificaciones y palabras clave
- **API REST**: Endpoints completos con Django REST Framework
- **Notificaciones**: Soporte para Telegram y Discord
- **Tareas Programadas**: Scraping automático con django-crontab
- **Idempotencia**: Prevención de productos duplicados basada en URL
- **Tests Comprehensivos**: Cobertura completa de testing
- **Base de Datos**: SQLite para prototipado, escalable a PostgreSQL/MySQL

## 📋 Requisitos

- Python 3.8+
- Django 5.2+
- Django REST Framework
- SQLite (incluido con Python)

## 🛠️ Instalación

### 1. Clonar el repositorio y configurar entorno virtual

```bash
cd Dropshiping
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install django djangorestframework django-crontab django-filter requests python-telegram-bot
```

### 3. Configurar base de datos

```bash
python manage.py migrate
```

### 4. (Opcional) Crear superusuario

```bash
python manage.py createsuperuser
```

## ⚙️ Configuración

### Variables de Entorno (Opcional)

Crear archivo `.env` en el directorio raíz:

```env
# Telegram Bot (opcional)
TELEGRAM_BOT_TOKEN=tu_token_de_bot_telegram
TELEGRAM_CHAT_ID=tu_chat_id

# Discord Webhook (opcional)
DISCORD_WEBHOOK_URL=tu_webhook_de_discord

# Django (opcional)
SECRET_KEY=tu_secret_key_personalizada
DEBUG=True
```

### Configuración en settings.py

Las notificaciones se configuran en `dropship_bot/settings.py`:

```python
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = 'tu_token_aqui'
TELEGRAM_CHAT_ID = 'tu_chat_id_aqui'

# Discord Webhook Configuration  
DISCORD_WEBHOOK_URL = 'tu_webhook_url_aqui'
```

## 🚀 Uso

### 1. Iniciar el servidor

```bash
python manage.py runserver
```

### 2. Endpoints disponibles

#### API Principal
- `GET /api/products/` - Listar productos con filtros
- `POST /api/products/` - Crear producto
- `GET /api/products/{id}/` - Detalle de producto
- `PUT/PATCH /api/products/{id}/` - Actualizar producto
- `DELETE /api/products/{id}/` - Eliminar producto

#### Endpoints Especiales
- `GET /api/products/stats/` - Estadísticas de productos
- `GET /api/products/recent/` - Productos recientes (24h)
- `GET /api/products/by_platform/?platform=aliexpress` - Productos por plataforma

#### Health Check
- `GET /health/` - Health check simple
- `GET /api/health/status/` - Health check detallado

### 3. Filtros disponibles

Los endpoints soportan los siguientes parámetros de filtro:

```
GET /api/products/?min_price=10&max_price=100&keywords=smartphone,electronics&max_shipping_days=20&min_rating=4.0
```

- `min_price` - Precio mínimo
- `max_price` - Precio máximo  
- `keywords` - Palabras clave (separadas por coma)
- `max_shipping_days` - Máximo días de envío
- `min_rating` - Calificación mínima
- `platforms` - Plataformas (separadas por coma)
- `categories` - Categorías (separadas por coma)
- `search` - Búsqueda en título y categoría
- `ordering` - Ordenamiento: `created_at`, `-created_at`, `price`, `-price`, `rating`, `-rating`

### 4. Comandos de gestión

#### Scraping manual
```bash
# Scrapear 5 productos de todas las plataformas
python manage.py scrape_products

# Scrapear 10 productos de plataforma específica
python manage.py scrape_products --platform mock --count 10

# Modo de prueba (no guarda en DB)
python manage.py scrape_products --dry-run
```

#### Gestión de tareas cron
```bash
# Agregar tareas cron al sistema
python manage.py manage_cron add

# Ver tareas cron actuales  
python manage.py manage_cron show

# Probar funciones cron manualmente
python manage.py manage_cron test

# Remover tareas cron
python manage.py manage_cron remove
```

#### Tests
```bash
# Ejecutar todos los tests
python manage.py test products

# Tests específicos
python manage.py test products.tests.ProductModelTest
python manage.py test products.tests.APITest
```

## 🔧 Arquitectura

### Estructura del proyecto

```
dropship_bot/
├── manage.py                    # Script principal de Django
├── requirements.txt             # Dependencias Python
├── db.sqlite3                  # Base de datos SQLite
├── .env.example                # Ejemplo de configuración
├── Dockerfile                  # Configuración Docker
├── docker-compose.yml          # Configuración Docker Compose
├── docker-compose.prod.yml     # Configuración para producción
├── nginx.conf                  # Configuración Nginx
├── deploy.sh                   # Script de despliegue automatizado
├── utils.ps1                   # Utilidades PowerShell (Windows)
├── maintenance.md              # Scripts de monitoreo y mantenimiento
├── MANUAL_USUARIO.md           # Manual del usuario
├── MANUAL_TECNICO.md           # Manual técnico
├── INSTALACION.md              # Guía de instalación
├── dropship_bot/          # Configuración principal de Django
│   ├── settings.py        # Configuraciones
│   ├── urls.py           # URLs principales
│   └── ...
├── products/             # Aplicación principal
│   ├── models.py         # Modelo Product
│   ├── views.py          # ViewSets de DRF
│   ├── serializers.py    # Serializers de DRF
│   ├── urls.py           # URLs de la app
│   ├── signals.py        # Señales de Django
│   ├── cron.py           # Tareas programadas
│   ├── services/         # Servicios modulares
│   │   ├── scraper.py    # Sistema de scraping
│   │   ├── filters.py    # Sistema de filtros
│   │   ├── notifications.py # Sistema de notificaciones
│   │   └── product_manager.py # Gestión de productos
│   ├── management/commands/ # Comandos personalizados
│   └── tests.py          # Tests unitarios
└── data/                 # Directorio para archivos de datos
```

### Componentes principales

#### 1. Sistema de Scraping (`services/scraper.py`)
- **BaseScraper**: Clase abstracta para scrapers
- **MockScraper**: Scraper de prueba con datos mock
- **AliExpressScraper**: Scraper para AliExpress (básico)
- **ScraperFactory**: Factory pattern para crear scrapers

#### 2. Sistema de Filtros (`services/filters.py`)
- **ProductFilter**: Clase para filtros complejos
- Soporte para QuerySets de Django y listas Python
- Filtros por precio, palabras clave, envío, calificación, plataforma

#### 3. Gestión de Productos (`services/product_manager.py`)
- **ProductManager**: Gestión con idempotencia
- Validación de datos
- Importación en lotes
- Deduplicación

#### 4. Notificaciones (`services/notifications.py`)
- **TelegramNotificationService**: Notificaciones por Telegram
- **DiscordNotificationService**: Notificaciones por Discord  
- **NotificationManager**: Gestor unificado
- Notificaciones automáticas al crear productos

### 5. Tareas Programadas

Configuradas en `settings.py`:

```python
CRONJOBS = [
    ('*/30 * * * *', 'products.cron.scrape_products'),        # Cada 30 minutos
    ('0 2 * * *', 'products.cron.cleanup_old_products'),      # Diario a las 2 AM
    ('*/15 * * * *', 'products.cron.health_check_cron'),      # Cada 15 minutos
]
```

## 📊 Ejemplos de uso

### 1. Obtener productos con filtros

```bash
curl "http://localhost:8000/api/products/?min_price=20&max_price=100&keywords=smartphone&max_shipping_days=15"
```

### 2. Obtener estadísticas

```bash
curl "http://localhost:8000/api/products/stats/"
```

Respuesta:
```json
{
    "total_products": 150,
    "average_price": "45.67",
    "min_price": "5.99",
    "max_price": "299.99",
    "platforms": ["mock_aliexpress", "aliexpress"],
    "categories": ["Electronics", "Home & Garden", "Sports"],
    "products_today": 25,
    "products_this_week": 89
}
```

### 3. Health check

```bash
curl "http://localhost:8000/api/health/status/"
```

Respuesta:
```json
{
    "status": "ok",
    "timestamp": "2025-09-29T10:30:00Z",
    "database": "ok", 
    "products_count": 150,
    "last_scrape": "2025-09-29T10:25:00Z"
}
```

## 🧪 Testing

El proyecto incluye tests comprehensivos:

- **ProductModelTest**: Tests del modelo Product
- **ScraperTest**: Tests del sistema de scraping
- **FilterTest**: Tests del sistema de filtros
- **ProductManagerTest**: Tests de gestión de productos
- **APITest**: Tests de la API REST
- **NotificationTest**: Tests del sistema de notificaciones
- **IntegrationTest**: Tests de integración

```bash
# Ejecutar todos los tests
python manage.py test products

# Tests con cobertura (requiere coverage)
pip install coverage
coverage run --source='.' manage.py test products
coverage report
```

## 🔒 Seguridad

- URLs únicas previenen duplicados
- Validación de datos en serializers y ProductManager
- Rate limiting implícito en scrapers
- Manejo seguro de errores
- Logs comprehensivos

## 📈 Escalabilidad

### Para producción:

1. **Base de datos**: Cambiar a PostgreSQL/MySQL
2. **Cache**: Agregar Redis/Memcached  
3. **Queue**: Usar Celery en lugar de crontab
4. **Scraping**: Implementar rate limiting y proxies
5. **Monitoreo**: Agregar Sentry, New Relic
6. **Deployment**: Docker, Kubernetes, AWS/Azure

### Configuración de producción:

```python
# settings/production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dropship_bot',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

## 🐳 Despliegue con Docker

### Instalación rápida con Docker

1. **Clonar el repositorio**:
```bash
git clone <tu-repo>
cd dropshipping
```

2. **Configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Usar utilidades PowerShell (Windows)**:
```powershell
# Inicializar proyecto
.\utils.ps1 init

# Iniciar servicios
.\utils.ps1 start

# Ver estado
.\utils.ps1 status

# Ver logs
.\utils.ps1 logs
```

4. **O usar script bash (Linux/Mac)**:
```bash
# Hacer ejecutable
chmod +x deploy.sh

# Desplegar en desarrollo
./deploy.sh development

# Desplegar en producción
./deploy.sh production
```

### Comandos Docker útiles

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f app

# Acceder al shell de la aplicación
docker-compose exec app bash

# Acceder al shell de Django
docker-compose exec app python manage.py shell

# Ejecutar migraciones
docker-compose exec app python manage.py migrate

# Ejecutar tests
docker-compose exec app python manage.py test

# Detener servicios
docker-compose down
```

### Monitoreo y Mantenimiento

Ver `maintenance.md` para scripts de:
- Monitoreo automático del sistema
- Backups automatizados
- Limpieza de contenedores y logs
- Alertas por Telegram/Discord
- Configuración de cron jobs

## 🤝 Contribución

1. Fork del proyecto
2. Crear branch para feature (`git checkout -b feature/nueva-feature`)
3. Commit de cambios (`git commit -am 'Agregar nueva feature'`)
4. Push al branch (`git push origin feature/nueva-feature`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver `LICENSE` para más detalles.

## 🙋‍♂️ Soporte

Para preguntas y soporte:

1. Crear issue en GitHub
2. Revisar documentación y tests
3. Verificar logs en `dropship_bot.log`

## 🚧 Roadmap

- [ ] Integración real con AliExpress API
- [ ] Scraper para Amazon
- [ ] Machine Learning para predicción de precios
- [ ] Dashboard web con Django Admin personalizado
- [ ] Exportación a CSV/Excel
- [ ] Integración con Shopify/WooCommerce
- [ ] Análisis de competencia
- [ ] Sistema de alertas avanzado

---

**Desarrollado con ❤️ usando Django y Python**
  
---

## 🛒 Productos Reales de AliExpress

Desde octubre 2025, el sistema utiliza productos REALES de AliExpress con URLs verificadas y datos actualizados. Esto garantiza que los productos mostrados en el dashboard y API existen y pueden usarse para dropshipping real.

**Ventajas:**
- URLs válidas y comprobadas
- Datos de precio, categoría, envío y rating realistas
- Listos para exportar y usar en tiendas reales

**Ejemplo de producto real:**
```json
{
    "title": "Auriculares Inalámbricos Bluetooth 5.0 TWS",
    "price": 12.45,
    "url": "https://es.aliexpress.com/item/1005001929715471.html",
    "category": "Electronics",
    "rating": 4.3,
    "shipping_time": 15
}
```

## 👤 Script fácil para usuarios finales

El archivo `easy_dropship.py` permite a cualquier usuario filtrar, buscar y exportar productos reales desde la terminal, sin necesidad de conocimientos técnicos ni acceso al dashboard web.

**Características:**
- Menú interactivo por consola
- Filtros por precio, categoría, rating y envío
- Exportación a CSV
- URLs listas para dropshipping

**Ejemplo de uso:**
```bash
python easy_dropship.py
```

Sigue las instrucciones en pantalla para buscar productos y exportar resultados.

---