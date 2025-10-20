# 🤖 Dropshipping Assistant Bot# Dropship Bot - Asistente de Dropshipping



## 📋 DescripciónUn asistente modular de dropshipping construido con Django que proporciona scraping automatizado, filtrado inteligente, persistencia de datos y notificaciones en tiempo real.



Bot automatizado de dropshipping que genera productos realistas y los envía automáticamente a Discord. Incluye interfaz web HTTPS para control y monitoreo.## 🚀 Características



![Status](https://img.shields.io/badge/Status-Funcionando-brightgreen)- **Scraping Modular**: Sistema extensible para scrapear productos de múltiples plataformas

![Python](https://img.shields.io/badge/Python-3.13-blue)- **Filtrado Inteligente**: Filtros avanzados por precio, categoría, tiempo de envío, calificaciones y palabras clave

![Django](https://img.shields.io/badge/Django-5.2-green)- **API REST**: Endpoints completos con Django REST Framework

![License](https://img.shields.io/badge/License-MIT-yellow)- **Notificaciones**: Soporte para Telegram y Discord

- **Tareas Programadas**: Scraping automático con django-crontab

## 🚀 Características Principales- **Idempotencia**: Prevención de productos duplicados basada en URL

- **Tests Comprehensivos**: Cobertura completa de testing

### ✅ Bot de Dropshipping- **Base de Datos**: SQLite para prototipado, escalable a PostgreSQL/MySQL

- **Generación automática** de productos realistas

- **Categorías**: Gaming, Accesorios, Audio## 📋 Requisitos

- **Datos completos**: Precios, ratings, ventas, stock

- **URLs realistas** de AliExpress- Python 3.8+

- Django 5.2+

### 📱 Integración Discord- Django REST Framework

- **Webhooks configurados** para envío automático- SQLite (incluido con Python)

- **Embeds profesionales** con branding

- **Información completa** por producto## 🛠️ Instalación

- **Envío instantáneo** al ejecutar

### 1. Clonar el repositorio y configurar entorno virtual

### 🌐 Interfaz Web HTTPS

- **Panel de control** moderno y responsive```bash

- **Ejecución desde navegador** con un cliccd Dropshiping

- **Dashboard completo** con analyticspython -m venv .venv

- **Certificados SSL** para desarrollo

# Windows

### 🔧 Arquitectura Técnica.venv\Scripts\activate

- **Django 5.2** como backend

- **Werkzeug** para servidor HTTPS# Linux/Mac

- **REST Framework** para APIssource .venv/bin/activate

- **SQLite** como base de datos```



## 📦 Instalación### 2. Instalar dependencias



### Prerrequisitos```bash

```bashpip install django djangorestframework django-crontab django-filter requests python-telegram-bot

Python 3.13+```

Git

```### 3. Configurar base de datos



### Clonar Repositorio```bash

```bashpython manage.py migrate

git clone https://github.com/Velazquezadrian/dropshipping-assistant.git```

cd dropshipping-assistant

```### 4. (Opcional) Crear superusuario



### Configurar Entorno```bash

```bashpython manage.py createsuperuser

# Crear entorno virtual```

python -m venv .venv

## ⚙️ Configuración

# Activar entorno (Windows)

.venv\Scripts\activate### Variables de Entorno (Opcional)



# Instalar dependenciasCrear archivo `.env` en el directorio raíz:

pip install -r requirements.txt

``````env

# Telegram Bot (opcional)

### Configurar Base de DatosTELEGRAM_BOT_TOKEN=tu_token_de_bot_telegram

```bashTELEGRAM_CHAT_ID=tu_chat_id

python manage.py migrate

```# Discord Webhook (opcional)

DISCORD_WEBHOOK_URL=tu_webhook_de_discord

### Generar Certificados SSL

```bash# Django (opcional)

python generar_ssl.pySECRET_KEY=tu_secret_key_personalizada

```DEBUG=True

```

## 🚀 Uso

### Configuración en settings.py

### Servidor Web HTTPS

```bashLas notificaciones se configuran en `dropship_bot/settings.py`:

python manage.py runserver_plus --cert-file localhost.crt --key-file localhost.key 127.0.0.1:8443

``````python

# Telegram Bot Configuration

Accede a: `https://127.0.0.1:8443/`TELEGRAM_BOT_TOKEN = 'tu_token_aqui'

TELEGRAM_CHAT_ID = 'tu_chat_id_aqui'

### Bot de Línea de Comandos

```bash# Discord Webhook Configuration  

# Bot optimizado para webDISCORD_WEBHOOK_URL = 'tu_webhook_url_aqui'

python bot_web.py```



# Bot completo con logging## 🚀 Uso

python bot_dropshipping_final.py

```### 1. Iniciar el servidor



## 🌐 URLs Disponibles```bash

python manage.py runserver

| Endpoint | Descripción |```

|----------|-------------|

| `https://127.0.0.1:8443/` | 🏠 Página principal |### 2. Endpoints disponibles

| `https://127.0.0.1:8443/dashboard/` | 📊 Dashboard completo |

| `https://127.0.0.1:8443/finder/` | 🔍 Buscador de productos |#### API Principal

| `https://127.0.0.1:8443/admin/` | 🔧 Panel administrativo |- `GET /api/products/` - Listar productos con filtros

| `https://127.0.0.1:8443/api/execute-bot/` | 🤖 API del bot |- `POST /api/products/` - Crear producto

- `GET /api/products/{id}/` - Detalle de producto

## 📊 Productos Generados- `PUT/PATCH /api/products/{id}/` - Actualizar producto

- `DELETE /api/products/{id}/` - Eliminar producto

El bot genera productos en 3 categorías principales:

#### Endpoints Especiales

### 🎮 Gaming- `GET /api/products/stats/` - Estadísticas de productos

- Mouse gaming RGB- `GET /api/products/recent/` - Productos recientes (24h)

- Teclados mecánicos- `GET /api/products/by_platform/?platform=aliexpress` - Productos por plataforma

- Headsets profesionales

- Webcams HD#### Health Check

- Mouse pads XXL- `GET /health/` - Health check simple

- `GET /api/health/status/` - Health check detallado

### 🔌 Accesorios

- Cables USB-C### 3. Filtros disponibles

- Cargadores inalámbricos

- Power banksLos endpoints soportan los siguientes parámetros de filtro:

- Adaptadores Bluetooth

- Hubs USB```

GET /api/products/?min_price=10&max_price=100&keywords=smartphone,electronics&max_shipping_days=20&min_rating=4.0

### 🎵 Audio```

- Auriculares inalámbricos

- Speakers Bluetooth- `min_price` - Precio mínimo

- Micrófonos- `max_price` - Precio máximo  

- Soundbars- `keywords` - Palabras clave (separadas por coma)

- `max_shipping_days` - Máximo días de envío

## ⚙️ Configuración- `min_rating` - Calificación mínima

- `platforms` - Plataformas (separadas por coma)

### Discord Webhook- `categories` - Categorías (separadas por coma)

El webhook de Discord está preconfigurado. Para cambiarlo, edita:- `search` - Búsqueda en título y categoría

- `ordering` - Ordenamiento: `created_at`, `-created_at`, `price`, `-price`, `rating`, `-rating`

```python

# bot_dropshipping_final.py o bot_web.py### 4. Comandos de gestión

self.discord_webhook = "TU_WEBHOOK_AQUI"

```#### Scraping manual

```bash

### Variables de Entorno# Scrapear 5 productos de todas las plataformas

Crea un archivo `.env`:python manage.py scrape_products



```env# Scrapear 10 productos de plataforma específica

SECRET_KEY=tu_secret_key_aquipython manage.py scrape_products --platform mock --count 10

DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1# Modo de prueba (no guarda en DB)

```python manage.py scrape_products --dry-run

```

## 🏗️ Arquitectura

#### Gestión de tareas cron

``````bash

dropshipping-assistant/# Agregar tareas cron al sistema

├── 🤖 bot_dropshipping_final.py    # Bot principal con loggingpython manage.py manage_cron add

├── 🌐 bot_web.py                   # Bot optimizado para web

├── 📋 README_FINAL.md              # Documentación detallada# Ver tareas cron actuales  

├── 🏆 PROYECTO_COMPLETADO.txt      # Resumen del proyectopython manage.py manage_cron show

├── 🔧 manage.py                    # Django management

├── ⚙️ requirements.txt             # Dependencias# Probar funciones cron manualmente

├── 🔐 generar_ssl.py               # Generador de certificadospython manage.py manage_cron test

├── 📁 dropship_bot/                # Configuración Django

├── 📦 products/                    # App principal# Remover tareas cron

│   ├── 🏠 home_views.py           # Vista principalpython manage.py manage_cron remove

│   ├── 📊 dashboard_views.py      # Dashboard```

│   ├── 🔍 views.py                # APIs

│   └── 📱 models.py               # Modelos de datos#### Tests

└── 📄 static/                      # Archivos estáticos```bash

```# Ejecutar todos los tests

python manage.py test products

## 🎯 Casos de Uso

# Tests específicos

### 1. Demostración de Productopython manage.py test products.tests.ProductModelTest

- Ejecutar desde interfaz webpython manage.py test products.tests.APITest

- Mostrar productos generados```

- Verificar envío a Discord

## 🔧 Arquitectura

### 2. Desarrollo y Testing

- Usar bot de línea de comandos### Estructura del proyecto

- Modificar categorías de productos

- Probar nuevas integraciones```

dropship_bot/

### 3. Presentación Profesional├── manage.py                    # Script principal de Django

- Interfaz web HTTPS├── requirements.txt             # Dependencias Python

- Dashboard con métricas├── db.sqlite3                  # Base de datos SQLite

- Documentación completa├── .env.example                # Ejemplo de configuración

├── Dockerfile                  # Configuración Docker

## 🛠️ Desarrollo├── docker-compose.yml          # Configuración Docker Compose

├── docker-compose.prod.yml     # Configuración para producción

### Estructura del Código├── nginx.conf                  # Configuración Nginx

- **MVC Pattern** con Django├── deploy.sh                   # Script de despliegue automatizado

- **Separation of Concerns** entre bot y web├── utils.ps1                   # Utilidades PowerShell (Windows)

- **RESTful APIs** para integración├── maintenance.md              # Scripts de monitoreo y mantenimiento

- **Responsive Design** para móviles├── MANUAL_USUARIO.md           # Manual del usuario

├── MANUAL_TECNICO.md           # Manual técnico

### Testing├── INSTALACION.md              # Guía de instalación

```bash├── dropship_bot/          # Configuración principal de Django

# Test del bot web│   ├── settings.py        # Configuraciones

python bot_web.py│   ├── urls.py           # URLs principales

│   └── ...

# Test del endpoint├── products/             # Aplicación principal

curl -X POST https://127.0.0.1:8443/api/execute-bot/│   ├── models.py         # Modelo Product

```│   ├── views.py          # ViewSets de DRF

│   ├── serializers.py    # Serializers de DRF

## 📈 Métricas│   ├── urls.py           # URLs de la app

│   ├── signals.py        # Señales de Django

- ✅ **100% funcional** en desarrollo│   ├── cron.py           # Tareas programadas

- 📱 **Discord integrado** y probado│   ├── services/         # Servicios modulares

- 🌐 **HTTPS configurado** con certificados│   │   ├── scraper.py    # Sistema de scraping

- 📊 **6 productos** generados por ejecución│   │   ├── filters.py    # Sistema de filtros

- ⚡ **Tiempo de respuesta** < 5 segundos│   │   ├── notifications.py # Sistema de notificaciones

│   │   └── product_manager.py # Gestión de productos

## 🤝 Contribuir│   ├── management/commands/ # Comandos personalizados

│   └── tests.py          # Tests unitarios

1. Fork el proyecto└── data/                 # Directorio para archivos de datos

2. Crea una rama feature (`git checkout -b feature/nueva-feature`)```

3. Commit cambios (`git commit -am 'Agrega nueva feature'`)

4. Push a la rama (`git push origin feature/nueva-feature`)### Componentes principales

5. Abre un Pull Request

#### 1. Sistema de Scraping (`services/scraper.py`)

## 📞 Soporte- **BaseScraper**: Clase abstracta para scrapers

- **MockScraper**: Scraper de prueba con datos mock

- 📧 **Issues**: [GitHub Issues](https://github.com/Velazquezadrian/dropshipping-assistant/issues)- **AliExpressScraper**: Scraper para AliExpress (básico)

- 📖 **Documentación**: Ver `README_FINAL.md`- **ScraperFactory**: Factory pattern para crear scrapers

- 🎯 **Wiki**: Próximamente

#### 2. Sistema de Filtros (`services/filters.py`)

## 📄 Licencia- **ProductFilter**: Clase para filtros complejos

- Soporte para QuerySets de Django y listas Python

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.- Filtros por precio, palabras clave, envío, calificación, plataforma



## 🏆 Estado del Proyecto#### 3. Gestión de Productos (`services/product_manager.py`)

- **ProductManager**: Gestión con idempotencia

**✅ PROYECTO COMPLETADO Y FUNCIONAL**- Validación de datos

- Importación en lotes

- 🤖 Bot funcionando al 100%- Deduplicación

- 📱 Discord integrado exitosamente  

- 🌐 Interfaz web HTTPS operativa#### 4. Notificaciones (`services/notifications.py`)

- 📊 Sistema de logging completo- **TelegramNotificationService**: Notificaciones por Telegram

- 🎯 Listo para producción/demostración- **DiscordNotificationService**: Notificaciones por Discord  

- **NotificationManager**: Gestor unificado

---- Notificaciones automáticas al crear productos



**Desarrollado con ❤️ para automatización de dropshipping**### 5. Tareas Programadas

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