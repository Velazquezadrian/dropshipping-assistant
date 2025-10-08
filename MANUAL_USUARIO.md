# Manual de Usuario - Dropship Bot# 📖 Manual de Usuario - Sistema de Dropshipping v2.0



## 🚀 Introducción## 🎯 Introducción



Dropship Bot es un sistema automatizado para encontrar productos reales de AliExpress con filtros avanzados. El sistema scrappea productos en tiempo real y proporciona una interfaz web fácil de usar.¡Bienvenido al sistema de dropshipping automatizado v2.0! Esta aplicación te ayuda a encontrar productos rentables de diferentes plataformas de e-commerce como AliExpress.



## 🎯 Características Principales### 🌟 Nuevas Funcionalidades v2.0



- ✅ **Productos Reales**: Scraping directo desde AliExpress- **🖥️ Dashboard Web**: Interfaz gráfica completa con Bootstrap 5

- ✅ **Filtros Avanzados**: Por precio, envío, rating- **⚡ Scraping Asíncrono**: Procesos en segundo plano con Celery

- ✅ **Interfaz Web**: Fácil de usar, responsive- **📋 Sistema de Jobs**: Seguimiento y cancelación de trabajos de scraping

- ✅ **API REST**: Para integración con otras aplicaciones- **📊 Analytics Avanzados**: Gráficos interactivos con Chart.js

- ✅ **HTTPS Seguro**: Conexión encriptada- **👁️ Monitoreo en Tiempo Real**: Con Flower para supervisar tareas

- ✅ **Sistema de Fallback**: Funciona aunque AliExpress bloquee- **🔔 Notificaciones Mejoradas**: Sistema automático con plantillas personalizadas



## 🛠️ Instalación Rápida### ¿Qué hace este sistema?



### 1. Prerrequisitos- 🔍 **Busca productos automáticamente** en diferentes plataformas

- Python 3.8 o superior- 📊 **Analiza precios y tendencias** para encontrar oportunidades

- Git (para clonar el repositorio)- 🔔 **Te notifica** cuando encuentra productos interesantes

- 📈 **Proporciona estadísticas** para tomar mejores decisiones

### 2. Configuración- 🖥️ **Dashboard web interactivo** para gestión visual

```bash- ⚡ **Procesos asíncronos** que no bloquean la aplicación

# Clonar repositorio

git clone https://github.com/Velazquezadrian/dropshipping-assistant.git---

cd dropshipping-assistant

## 🚀 Primeros Pasos

# Crear entorno virtual

python -m venv .venv### 1. Acceso al Sistema



# Activar entorno (Windows)Una vez que el sistema esté instalado y funcionando, puedes acceder a través de:

.venv\Scripts\activate

- **🖥️ Dashboard Web**: http://localhost:8000/ (¡NUEVO!)

# Instalar dependencias- **📊 Dashboard de Analytics**: http://localhost:8000/dashboard/ (¡NUEVO!)

pip install -r requirements.txt- **👁️ Monitor de Tareas (Flower)**: http://localhost:8001/ (¡NUEVO!)

- **API REST**: http://localhost:8000/api/products/

# Configurar base de datos- **Panel de Administración**: http://localhost:8000/admin/

python manage.py migrate- **Health Check**: http://localhost:8000/health/

```

### 2. Dashboard Web - Tu Centro de Control

### 3. Iniciar el Sistema

```bash**🎯 ¡Novedad v2.0!** Ahora tienes una interfaz web completa:

# Servidor HTTPS (Recomendado)

python manage.py runserver_plus --cert-file certs/cert.pem --key-file certs/key.pem 127.0.0.1:8443#### Página Principal (http://localhost:8000/)

- Vista general del sistema

# O servidor HTTP (desarrollo)- Estadísticas en tiempo real

python manage.py runserver 127.0.0.1:8000- Acceso rápido a todas las funciones

```

#### Dashboard de Analytics (http://localhost:8000/dashboard/)

## 🌐 Uso de la Interfaz Web- 📊 **Gráficos Interactivos**: Tendencias de precios y productos

- 📈 **Métricas en Tiempo Real**: Total de productos, precios promedio

### Acceder al Sistema- 🔍 **Filtros Avanzados**: Por categoría, plataforma, fecha

- **HTTPS**: https://127.0.0.1:8443/real-filter-ui/- 📱 **Responsive**: Funciona perfecto en móviles y tablets

- **HTTP**: http://127.0.0.1:8000/real-filter-ui/

#### Monitor de Tareas (http://localhost:8001/)

### Búsqueda de Productos- ⚡ **Flower Dashboard**: Monitorea trabajos de scraping en tiempo real

- 📋 **Estado de Jobs**: Ve qué tareas están corriendo, completadas o fallaron

1. **Keywords**: Introduce palabras clave en inglés- 🔧 **Control Total**: Cancela o reinicia tareas según necesites

   - Ejemplos: `wireless mouse gaming`, `bluetooth headphones`, `phone case`

### 3. Verificar que el Sistema Funciona

2. **Filtro de Precio**:

   - **Precio Mínimo**: Ej. 15 USDVisita http://localhost:8000/health/ en tu navegador. Deberías ver:

   - **Precio Máximo**: Ej. 45 USD

   - **Moneda**: USD (por defecto)```json

{

3. **Filtro de Envío**:    "status": "ok",

   - **Días Máximos**: Ej. 30 días    "message": "Dropship Bot API está funcionando"

}

4. **Límite de Productos**:```

   - **Cantidad**: Ej. 5 productos

---

5. **Buscar**: Haz clic en "Buscar Productos"

## 🛍️ Gestión de Productos

### Interpretación de Resultados

### Ver Productos

#### Indicadores de Estado

- 🟢 **Verde**: Productos reales de AliExpressPara ver todos los productos disponibles:

- 🟡 **Amarillo**: Productos de fallback (AliExpress bloqueó)

**Opción 1: Navegador Web**

#### Información del Producto- Ve a: http://localhost:8000/api/products/

- **Título**: Nombre del producto

- **Precio**: En USD**Opción 2: Línea de comandos (curl)**

- **Rating**: Calificación de 1-5 estrellas```bash

- **Envío**: Días estimados de entregacurl http://localhost:8000/api/products/

- **URL**: Enlace directo al producto```



## 📡 Uso de la API### Ejemplo de respuesta:

```json

### Endpoints Disponibles{

    "count": 25,

#### 1. Búsqueda de Productos    "next": "http://localhost:8000/api/products/?page=2",

```bash    "previous": null,

POST https://127.0.0.1:8443/real-filter/    "results": [

Content-Type: application/json        {

            "id": 1,

{            "title": "Smartphone Android 128GB",

  "keywords": "wireless mouse gaming",            "price": "299.99",

  "min_price": 15,            "url": "https://example-aliexpress.com/item/smartphone-1234",

  "max_price": 45,            "image": "https://example.com/images/smartphone1.jpg",

  "currency": "USD",            "created_at": "2025-09-29T10:30:00Z",

  "max_shipping_days": 30,            "rating": "4.5",

  "limit": 5            "source_platform": "mock_aliexpress"

}        }

```    ]

}

#### 2. Información del Sistema```

```bash

GET https://127.0.0.1:8443/real-filter/info/---

```

## ⚡ Scraping Asíncrono - Lo Más Nuevo

#### 3. Test Rápido

```bash### 🎯 ¿Qué es el Scraping Asíncrono?

GET https://127.0.0.1:8443/real-filter/quick-test/

```En la v2.0 hemos implementado un sistema de scraping que corre en segundo plano, permitiéndote:

- 🚀 **Iniciar búsquedas sin esperar**: El proceso corre mientras haces otras cosas

### Ejemplo con curl- 📋 **Seguir el progreso**: Ve en tiempo real cómo avanza el scraping

```bash- ❌ **Cancelar trabajos**: Si cambias de opinión, cancela fácilmente

curl -X POST https://127.0.0.1:8443/real-filter/ \- 📊 **Historial completo**: Todos los trabajos quedan registrados

  -H "Content-Type: application/json" \

  -k \### 🚀 Cómo Usar el Scraping Asíncrono

  -d '{

    "keywords": "bluetooth headphones",#### Desde el Dashboard Web:

    "min_price": 20,1. Ve a http://localhost:8000/dashboard/

    "max_price": 60,2. Busca el botón **"Iniciar Scraping Asíncrono"**

    "currency": "USD",3. Configura los parámetros (cantidad de productos, filtros)

    "max_shipping_days": 25,4. ¡Haz clic y listo! El trabajo se ejecutará en segundo plano

    "limit": 3

  }'#### Desde la API:

```

**Iniciar un trabajo de scraping:**

### Respuesta de la API```bash

```jsoncurl -X POST http://localhost:8000/api/scrape/async/ \

{  -H "Content-Type: application/json" \

  "products": [  -d '{"count": 50, "platforms": ["aliexpress"]}'

    {```

      "title": "Wireless Gaming Mouse RGB",

      "price": "$29.99",**Ver el estado del trabajo:**

      "currency": "USD",```bash

      "url": "https://aliexpress.com/item/...",curl http://localhost:8000/api/scrape/status/

      "image_url": "https://ae01.alicdn.com/...",```

      "rating": 4.5,

      "rating_count": 1250,**Listar todos los trabajos:**

      "shipping_days": 15,```bash

      "category": "Electronics"curl http://localhost:8000/api/scrape/jobs/

    }```

  ],

  "real_products": true,**Cancelar un trabajo específico:**

  "source": "aliexpress_real",```bash

  "total_found": 3,curl -X POST http://localhost:8000/api/scrape/jobs/123/cancel/

  "filters_applied": {```

    "min_price": 20,

    "max_price": 60,### 📊 Estados de los Trabajos

    "max_shipping_days": 25

  }| Estado | Descripción | Acción |

}|--------|-------------|---------|

```| `PENDING` | ⏳ Esperando ejecutarse | - |

| `STARTED` | 🔄 Ejecutándose ahora | Puedes cancelar |

## 💡 Consejos de Uso| `SUCCESS` | ✅ Completado exitosamente | Ver resultados |

| `FAILURE` | ❌ Falló por algún error | Ver logs de error |

### Para Mejores Resultados| `REVOKED` | 🚫 Cancelado por usuario | - |

- **Keywords en inglés**: Los términos en inglés funcionan mejor

- **Palabras específicas**: "wireless mouse gaming" vs "mouse"### 🔔 Notificaciones Automáticas

- **Rangos de precio realistas**: No muy bajos ni muy altos

- **Paciencia**: El scraping real puede tomar 10-30 segundosCuando inicias un scraping asíncrono, el sistema te notificará automáticamente:

- ✅ **Al completarse**: "Se encontraron 50 nuevos productos"

### Keywords Recomendadas- ❌ **Si falla**: "Error en el scraping: detalles del problema"

- **Electrónicos**: `wireless mouse`, `bluetooth headphones`, `phone case`- 📊 **Resumen**: Estadísticas del trabajo realizado

- **Hogar**: `kitchen tools`, `home decor`, `led lights`

- **Deportes**: `fitness tracker`, `sports equipment`, `yoga mat`---

- **Moda**: `fashion accessories`, `jewelry`, `bags`

## 📊 Dashboard y Analytics

### Filtros Efectivos

- **Precio**: Rango de $10-$100 USD da mejores resultados### 🎨 Dashboard Principal

- **Envío**: 15-45 días es típico de AliExpress

- **Límite**: 3-10 productos para pruebas rápidasEl dashboard web te ofrece una experiencia visual completa:



## 🔍 Troubleshooting#### 📈 Gráficos Disponibles:

- **Productos por Día**: Ve cómo crece tu base de datos

### Problemas Comunes- **Distribución de Precios**: Histograma de rangos de precios

- **Productos por Plataforma**: Comparativa entre AliExpress, Amazon, etc.

#### 1. No Aparecen Productos- **Productos por Categoría**: ¿Qué categorías son más populares?

- **Causa**: AliExpress puede estar bloqueando- **Tendencias de Rating**: Calidad promedio de productos

- **Solución**: El sistema usa fallback automático

- **Acción**: Intenta keywords diferentes#### 📊 Métricas en Tiempo Real:

- Total de productos en la base de datos

#### 2. Tarda Mucho en Cargar- Precio promedio y rangos

- **Causa**: Scraping real toma tiempo- Productos agregados hoy/esta semana

- **Solución**: Normal, espera 10-30 segundos- Plataformas activas

- **Acción**: Reduce el límite de productos- Categorías disponibles



#### 3. Error de Conexión SSL#### 🔍 Funciones Interactivas:

- **Causa**: Certificado autofirmado- **Filtrar por fechas**: Ve productos de períodos específicos

- **Solución**: Acepta el certificado en el navegador- **Filtrar por categorías**: Enfócate en lo que te interesa

- **Acción**: Usa HTTP si es necesario- **Búsqueda en tiempo real**: Encuentra productos específicos

- **Exportar datos**: Descarga reportes en CSV/JSON

#### 4. Error 404

- **Causa**: Servidor no iniciado### 📱 Responsive Design

- **Solución**: Verifica que el servidor esté corriendo

- **Acción**: Ejecuta `python manage.py runserver_plus`El dashboard funciona perfectamente en:

- 💻 **Desktop**: Experiencia completa con todos los gráficos

### Logs y Debugging- 📱 **Móvil**: Optimizado para gestión sobre la marcha

- **Logs del servidor**: Mira la consola donde ejecutaste el servidor- 📟 **Tablet**: Perfecto para presentaciones y análisis

- **Network tab**: F12 en el navegador para ver requests

- **Test endpoints**: Usa `/real-filter/quick-test/` para verificar---



## 🚀 Casos de Uso## 🔍 Filtrado de Productos



### 1. Investigación de Mercado### Filtros Disponibles

```bash

# Buscar productos en categoría específicaPuedes filtrar productos usando los siguientes parámetros:

Keywords: "smartphone accessories"

Precio: $5-$50| Parámetro | Descripción | Ejemplo |

Envío: 30 días max|-----------|-------------|---------|

```| `min_price` | Precio mínimo | `min_price=20` |

| `max_price` | Precio máximo | `max_price=100` |

### 2. Análisis de Competencia| `keywords` | Palabras clave | `keywords=smartphone,android` |

```bash| `max_shipping_days` | Máximo días de envío | `max_shipping_days=15` |

# Productos similares a los tuyos| `min_rating` | Calificación mínima | `min_rating=4.0` |

Keywords: "leather wallet men"| `platforms` | Plataformas específicas | `platforms=aliexpress,amazon` |

Precio: $15-$35| `categories` | Categorías | `categories=Electronics,Home` |

Rating mínimo: 4.0+| `search` | Búsqueda general | `search=bluetooth` |

```

### Ejemplos Prácticos

### 3. Trending Products

```bash#### 1. Productos baratos y rápidos

# Productos populares```

Keywords: "trending gadgets 2025"http://localhost:8000/api/products/?max_price=50&max_shipping_days=10

Precio: $10-$100```

Envío: 20 días max

```#### 2. Electrónicos bien calificados

```

## 📞 Soportehttp://localhost:8000/api/products/?categories=Electronics&min_rating=4.0

```

### Tests Disponibles

```bash#### 3. Productos con palabras específicas

# Test completo del sistema```

python test_bot_real.pyhttp://localhost:8000/api/products/?keywords=wireless,bluetooth&min_rating=4.0

```

# Demo funcional

python demo_final_real.py#### 4. Rango de precio específico

```

# Verificación del bothttp://localhost:8000/api/products/?min_price=25&max_price=75

python verificar_bot_real.py```

```

---

### Información del Sistema

- **Versión**: Django 5.2.6## 📊 Estadísticas y Reportes

- **Python**: 3.8+

- **Base de datos**: SQLite### Ver Estadísticas Generales

- **Scraping**: BeautifulSoup + requests

**URL**: http://localhost:8000/api/products/stats/

---

**Ejemplo de respuesta**:

**¡Disfruta usando Dropship Bot para encontrar los mejores productos de AliExpress!** 🚀```json
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

### Ver Productos Recientes (últimas 24 horas)

**URL**: http://localhost:8000/api/products/recent/

---

## 🔔 Sistema de Notificaciones

### Configurar Notificaciones por Telegram

1. **Crear un Bot de Telegram**:
   - Habla con @BotFather en Telegram
   - Usa el comando `/newbot`
   - Guarda el token que te proporcione

2. **Obtener tu Chat ID**:
   - Envía un mensaje a tu bot
   - Ve a: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
   - Busca el "chat_id" en la respuesta

3. **Configurar en el sistema**:
   - Edita el archivo de configuración
   - Agrega tu token y chat ID

### Configurar Notificaciones por Discord

1. **Crear un Webhook en Discord**:
   - Ve a la configuración de tu servidor
   - Integrations → Webhooks → New Webhook
   - Copia la URL del webhook

2. **Configurar en el sistema**:
   - Agrega la URL del webhook en la configuración

### Tipos de Notificaciones

El sistema enviará notificaciones automáticamente cuando:
- ✅ Se encuentren nuevos productos
- 📊 Se complete un ciclo de scraping
- ⚠️ Ocurran errores importantes

---

## 🤖 Automatización y Gestión de Trabajos

### ⚡ Scraping Automático

El sistema busca productos nuevos automáticamente cada 30 minutos usando Celery. ¡No necesitas hacer nada, funciona solo!

### 📋 Gestión de Trabajos de Scraping

#### Ver todos los trabajos:
```bash
python manage.py manage_cron list
```

#### Iniciar scraping asíncrono desde comando:
```bash
python manage.py scrape_products --async --count 100
```

#### Ver estado de trabajos activos:
```bash
python manage.py manage_cron status
```

#### Cancelar trabajos específicos:
```bash
python manage.py manage_cron cancel --job-id 123
```

### 📊 Comandos de Gestión Avanzados

#### Limpiar trabajos antiguos:
```bash
python manage.py manage_cron cleanup --older-than 7
```

#### Reiniciar trabajos fallidos:
```bash
python manage.py manage_cron retry-failed
```

#### Estadísticas de trabajos:
```bash
python manage.py manage_cron stats
```

### 🔔 Gestión de Notificaciones

#### Probar notificaciones:
```bash
python manage.py manage_notifications test
```

#### Configurar plantillas personalizadas:
```bash
python manage.py manage_notifications setup-templates
```

#### Ver historial de notificaciones:
```bash
python manage.py manage_notifications history
```

### 🎛️ Monitoreo con Flower

Accede a http://localhost:8001/ para:
- 👁️ **Ver tareas en tiempo real**: Qué está ejecutándose ahora
- 📊 **Estadísticas de workers**: Rendimiento del sistema
- 🔄 **Controlar tareas**: Reiniciar, cancelar, o reprogramar
- 📈 **Gráficos de rendimiento**: Throughput y latencia

### 🔧 Agregar Productos Manualmente

#### Scraping tradicional (bloqueante):
```bash
python manage.py scrape_products --count 10
```

#### Para probar sin guardar:
```bash
python manage.py scrape_products --dry-run
```

#### Scraping específico por plataforma:
```bash
python manage.py scrape_products --platforms aliexpress --count 50
```

---

## 🎯 Casos de Uso Comunes

### 1. 🖥️ Gestión Visual con Dashboard

**Flujo recomendado para nuevos usuarios:**

1. **Accede al Dashboard**: http://localhost:8000/dashboard/
2. **Revisa estadísticas generales**: Ve tu situación actual
3. **Inicia scraping asíncrono**: Busca productos nuevos sin esperar
4. **Monitorea el progreso**: En el dashboard de Flower
5. **Analiza resultados**: Con los gráficos interactivos

### 2. 📊 Análisis de Mercado Completo

**Para análisis profundo de oportunidades:**

```bash
# 1. Inicia scraping masivo asíncrono
curl -X POST http://localhost:8000/api/scrape/async/ \
  -H "Content-Type: application/json" \
  -d '{"count": 200, "platforms": ["aliexpress"]}'

# 2. Mientras tanto, analiza datos existentes
# Ve al dashboard: http://localhost:8000/dashboard/

# 3. Exporta reportes específicos
curl "http://localhost:8000/api/products/?format=csv&min_rating=4.0&max_price=50"
```

### 3. 🔍 Encontrar Productos Rentables

**Objetivo**: Productos con buen precio y alta calificación

**Desde el Dashboard Web:**
1. Ve a http://localhost:8000/dashboard/
2. Usa filtros: Precio máximo $50, Rating mínimo 4.0
3. Analiza tendencias en los gráficos
4. Exporta lista de productos seleccionados

**Desde la API:**
```bash
curl "http://localhost:8000/api/products/?max_price=50&min_rating=4.0&max_shipping_days=20"
```

### 4. ⚡ Monitoreo en Tiempo Real

**Para seguimiento continuo:**

1. **Dashboard Principal**: http://localhost:8000/dashboard/
   - Métricas en tiempo real
   - Gráficos actualizados automáticamente
   
2. **Monitor de Tareas**: http://localhost:8001/
   - Estado de scraping asíncrono
   - Performance de workers
   
3. **Notificaciones Automáticas**:
   - Configura Telegram/Discord
   - Recibe alertas automáticas

### 5. 🛍️ Productos de Electrónicos Populares

**Objetivo**: Gadgets y electrónicos bien valorados

**Flujo completo:**
```bash
# 1. Busca específicamente electrónicos
curl -X POST http://localhost:8000/api/scrape/async/ \
  -H "Content-Type: application/json" \
  -d '{"count": 100, "categories": ["Electronics"], "min_rating": 4.2}'

# 2. Filtra por palabras clave
curl "http://localhost:8000/api/products/?categories=Electronics&min_rating=4.2&keywords=smart,wireless"

# 3. Analiza en el dashboard
# http://localhost:8000/dashboard/ → Filtrar por "Electronics"
```

### 6. 🚚 Productos de Envío Rápido

**Objetivo**: Productos que llegan rápido al cliente

```bash
curl "http://localhost:8000/api/products/?max_shipping_days=10&min_rating=4.0"
```

### 7. 💰 Productos de Bajo Costo

**Objetivo**: Productos baratos para márgenes altos

```bash
curl "http://localhost:8000/api/products/?max_price=25&min_rating=3.5"
```

### 8. 📈 Análisis de Tendencias

**Para entender el mercado:**

1. **Dashboard de Analytics**: Gráficos de tendencias de precios
2. **Comparativas por período**: Filtros de fecha en el dashboard
3. **Reportes exportables**: Descarga datos para Excel/análisis externo

---

## 🛠️ Solución de Problemas

### Problema: "No veo productos en el dashboard"

**Solución:**
1. **Inicia scraping asíncrono desde el dashboard**:
   - Ve a http://localhost:8000/dashboard/
   - Haz clic en "Iniciar Scraping Asíncrono"
   
2. **O desde línea de comandos**:
   ```bash
   python manage.py scrape_products --async --count 10
   ```
   
3. **Verifica en tiempo real**: http://localhost:8001/ (Flower)

### Problema: "El dashboard no carga"

**Solución:**
1. Verifica que todos los servicios estén corriendo:
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```
   
2. Revisa el health check: http://localhost:8000/health/
   
3. Verifica logs:
   ```bash
   docker-compose -f docker-compose.prod.yml logs app
   ```

### Problema: "Las tareas asíncronas no funcionan"

**Solución:**
1. **Verifica que Celery esté corriendo**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps celery
   ```
   
2. **Revisa el monitor de Flower**: http://localhost:8001/
   
3. **Verifica Redis**:
   ```bash
   docker-compose -f docker-compose.prod.yml ps redis
   ```
   
4. **Reinicia servicios si es necesario**:
   ```bash
   docker-compose -f docker-compose.prod.yml restart celery
   ```

### Problema: "Las notificaciones no llegan"

**Solución:**
1. **Verifica configuración en el dashboard**
2. **Prueba notificaciones**:
   ```bash
   python manage.py manage_notifications test
   ```
3. **Revisa logs de notificaciones**:
   ```bash
   tail -f logs/monitor.log | grep notification
   ```

### Problema: "Jobs de scraping se cancelan automáticamente"

**Solución:**
1. **Verifica memoria y CPU** en Flower: http://localhost:8001/
2. **Ajusta timeout en configuración**
3. **Reduce cantidad de productos por job**:
   ```bash
   curl -X POST http://localhost:8000/api/scrape/async/ \
     -d '{"count": 20}' -H "Content-Type: application/json"
   ```

### Problema: "El sistema está lento"

**Solución:**
1. **Verifica recursos en Flower**: http://localhost:8001/monitor
2. **Revisa health check**: http://localhost:8000/health/
3. **Optimiza base de datos**:
   ```bash
   python manage.py shell
   >>> from products.services.product_manager import ProductManager
   >>> ProductManager.cleanup_old_products(days=30)
   ```

### Problema: "Productos duplicados"

**Solución:**
El sistema previene duplicados automáticamente por URL. Si ves duplicados:
```bash
python manage.py shell
>>> from products.services.product_manager import ProductManager
>>> ProductManager.deduplicate_products()
```

### Problema: "No puedo acceder a Flower"

**Solución:**
1. **Verifica que el perfil monitoring esté activo**:
   ```bash
   docker-compose -f docker-compose.prod.yml --profile monitoring up -d
   ```
   
2. **Verifica puerto**: http://localhost:8001/
   
3. **Revisa logs de Flower**:
   ```bash
   docker-compose -f docker-compose.prod.yml logs flower
   ```

### 🚨 Comandos de Emergencia

#### Reiniciar todo el sistema:
```bash
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml --profile monitoring up -d
```

#### Limpiar jobs colgados:
```bash
python manage.py manage_cron cleanup --force
```

#### Verificar estado completo:
```bash
python manage.py manage_cron status --verbose
```

---

## 📱 Usando desde Aplicaciones Móviles

### Apps recomendadas para consumir la API:

**Android:**
- HTTP Shortcuts
- Tasker (para automatización)

**iOS:**
- Shortcuts
- HTTP Client

### Ejemplo de configuración en Shortcuts (iOS):

1. Crear nuevo Shortcut
2. Agregar acción "Get Contents of URL"
3. URL: `http://TU_IP:8000/api/products/?max_price=50`
4. Agregar acción "Get Value for" → results
5. Agregar acción "Show Notification"

---

## 💡 Tips y Mejores Prácticas

### ✅ Recomendaciones

1. **Revisa las estadísticas regularmente**: Te ayudan a entender qué productos están funcionando

2. **Usa filtros específicos**: En lugar de ver todos los productos, filtra por lo que realmente te interesa

3. **Configura notificaciones**: Te mantendrán informado sin necesidad de revisar constantemente

4. **Monitorea el health check**: Si está en "error", revisa los logs

### ⚠️ Limitaciones Actuales

1. **Datos de Prueba**: En desarrollo usa datos mock. En producción se conecta a APIs reales de AliExpress

2. **Rate Limiting**: Para proteger las APIs, hay límites en la frecuencia de scraping

3. **Dependencias Externas**: Requiere Redis y PostgreSQL para funcionar completamente

### 🌟 Funcionalidades Disponibles

✅ **Interfaz Web Completa**: Dashboard interactivo con Bootstrap 5  
✅ **Scraping Asíncrono**: Procesos en segundo plano con Celery  
✅ **Analytics Avanzados**: Gráficos interactivos con Chart.js  
✅ **Sistema de Notificaciones**: Telegram y Discord integrados  
✅ **Monitoreo en Tiempo Real**: Dashboard de Flower  
✅ **API REST Completa**: Todos los endpoints documentados  
✅ **Testing Automático**: Suite completa de pruebas  
✅ **Deploy con Docker**: Configuración de producción lista

---

## 📞 Soporte y Recursos

### 🔗 Enlaces Importantes

| Recurso | URL | Descripción |
|---------|-----|-------------|
| 🖥️ **Dashboard Principal** | http://localhost:8000/ | Página de inicio y resumen |
| 📊 **Analytics Dashboard** | http://localhost:8000/dashboard/ | Gráficos y estadísticas |
| 👁️ **Monitor de Tareas (Flower)** | http://localhost:8001/ | Monitoreo de Celery |
| 🔧 **Panel Admin** | http://localhost:8000/admin/ | Administración Django |
| ❤️ **Health Check** | http://localhost:8000/health/ | Estado del sistema |
| 📄 **API Docs** | http://localhost:8000/api/ | Documentación API |

### 🛠️ Diagnóstico Rápido

#### Si algo no funciona, revisa EN ESTE ORDEN:

1. **Health Check**: http://localhost:8000/health/
   - ✅ Verde = Todo bien
   - ❌ Rojo = Hay problemas

2. **Dashboard de Servicios**: 
   ```bash
   docker-compose -f docker-compose.prod.yml ps
   ```

3. **Monitor de Tareas**: http://localhost:8001/
   - Ve si Celery está activo
   - Revisa jobs fallidos

4. **Logs del Sistema**:
   ```bash
   tail -f logs/monitor.log
   tail -f dropship_bot.log
   ```

### 🧪 Testing y Validación

#### Verificar que todo funcione:
```bash
# Test básico del sistema
python manage.py test products

# Test específico de scraping asíncrono
python manage.py test products.tests.test_async_scraping

# Test de notificaciones
python manage.py manage_notifications test
```

### 📊 Endpoints Clave para Desarrolladores

#### Scraping Asíncrono:
- `POST /api/scrape/async/` - Iniciar scraping
- `GET /api/scrape/status/` - Estado actual
- `GET /api/scrape/jobs/` - Lista de trabajos
- `POST /api/scrape/jobs/{id}/cancel/` - Cancelar trabajo

#### Analytics:
- `GET /api/products/stats/` - Estadísticas generales
- `GET /api/products/recent/` - Productos recientes
- `GET /dashboard/` - Dashboard web

#### Gestión:
- `GET /health/` - Estado del sistema
- `GET /api/products/?format=csv` - Exportar datos

### 📚 Documentación Adicional

- **Manual Técnico**: `MANUAL_TECNICO.md` (para desarrolladores)
- **README**: Instalación y configuración básica
- **Production Summary**: `PRODUCTION_SUMMARY.md` (para deploy)

### 🆘 Si necesitas ayuda:

1. **🩺 Diagnóstico automático**: 
   ```bash
   python manage.py manage_cron status --verbose
   ```

2. **📋 Información del sistema**:
   ```bash
   python manage.py shell
   >>> from products.services.notifications import NotificationService
   >>> NotificationService.system_info()
   ```

3. **🔍 Debug detallado**:
   ```bash
   # Activa logs detallados
   export DJANGO_LOG_LEVEL=DEBUG
   python manage.py runserver
   ```

### 📞 Información de contacto:
- 📧 **Email**: [tu-email@ejemplo.com]
- 💬 **Chat**: [tu-canal-de-soporte] 
- 📖 **Documentación**: README.md y MANUAL_TECNICO.md
- 🐛 **Issues**: [GitHub Issues]

---

## 🎯 Resumen de Funcionalidades v2.0

### ✨ Lo que puedes hacer AHORA:

✅ **Dashboard Web Completo**: Gestión visual con Bootstrap 5  
✅ **Scraping Asíncrono**: Trabajos en segundo plano con Celery  
✅ **Analytics Interactivos**: Gráficos con Chart.js  
✅ **Monitoreo en Tiempo Real**: Dashboard de Flower  
✅ **Sistema de Jobs**: Seguimiento completo de trabajos  
✅ **Notificaciones Automáticas**: Telegram y Discord integrados  
✅ **API REST Completa**: Todos los endpoints documentados  
✅ **Exportación de Datos**: CSV, JSON, Excel  
✅ **Testing Automático**: Suite completa de pruebas  
✅ **Deploy de Producción**: Docker Compose listo  

### 🚀 Flujo de Trabajo Recomendado:

1. **Ve al Dashboard**: http://localhost:8000/dashboard/
2. **Inicia scraping asíncrono** con los parámetros que necesites
3. **Monitorea el progreso** en Flower: http://localhost:8001/
4. **Analiza resultados** con los gráficos interactivos
5. **Exporta datos** para análisis externo
6. **Configura notificaciones** para estar siempre informado

---

**¡Feliz dropshipping con la v2.0! 🚀📊⚡**