# 📖 Manual de Usuario - Dropship Bot

## Bienvenido al Dropship Bot

Dropship Bot es tu asistente inteligente para gestionar productos de dropshipping. Esta herramienta te ayuda a encontrar, filtrar y gestionar productos de diferentes plataformas de manera automatizada.

---

## 🚀 Primeros Pasos

### 1. Acceso al Sistema

Una vez que el sistema esté instalado y funcionando, puedes acceder a través de:

- **API Web**: http://localhost:8000/api/products/
- **Panel de Administración**: http://localhost:8000/admin/
- **Health Check**: http://localhost:8000/health/

### 2. Verificar que el Sistema Funciona

Visita http://localhost:8000/health/ en tu navegador. Deberías ver:

```json
{
    "status": "ok",
    "message": "Dropship Bot API está funcionando"
}
```

---

## 🛍️ Gestión de Productos

### Ver Productos

Para ver todos los productos disponibles:

**Opción 1: Navegador Web**
- Ve a: http://localhost:8000/api/products/

**Opción 2: Línea de comandos (curl)**
```bash
curl http://localhost:8000/api/products/
```

### Ejemplo de respuesta:
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Smartphone Android 128GB",
            "price": "299.99",
            "url": "https://example-aliexpress.com/item/smartphone-1234",
            "image": "https://example.com/images/smartphone1.jpg",
            "created_at": "2025-09-29T10:30:00Z",
            "rating": "4.5",
            "source_platform": "mock_aliexpress"
        }
    ]
}
```

---

## 🔍 Filtrado de Productos

### Filtros Disponibles

Puedes filtrar productos usando los siguientes parámetros:

| Parámetro | Descripción | Ejemplo |
|-----------|-------------|---------|
| `min_price` | Precio mínimo | `min_price=20` |
| `max_price` | Precio máximo | `max_price=100` |
| `keywords` | Palabras clave | `keywords=smartphone,android` |
| `max_shipping_days` | Máximo días de envío | `max_shipping_days=15` |
| `min_rating` | Calificación mínima | `min_rating=4.0` |
| `platforms` | Plataformas específicas | `platforms=aliexpress,amazon` |
| `categories` | Categorías | `categories=Electronics,Home` |
| `search` | Búsqueda general | `search=bluetooth` |

### Ejemplos Prácticos

#### 1. Productos baratos y rápidos
```
http://localhost:8000/api/products/?max_price=50&max_shipping_days=10
```

#### 2. Electrónicos bien calificados
```
http://localhost:8000/api/products/?categories=Electronics&min_rating=4.0
```

#### 3. Productos con palabras específicas
```
http://localhost:8000/api/products/?keywords=wireless,bluetooth&min_rating=4.0
```

#### 4. Rango de precio específico
```
http://localhost:8000/api/products/?min_price=25&max_price=75
```

---

## 📊 Estadísticas y Reportes

### Ver Estadísticas Generales

**URL**: http://localhost:8000/api/products/stats/

**Ejemplo de respuesta**:
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

## 🤖 Automatización

### Scraping Automático

El sistema busca productos nuevos automáticamente cada 30 minutos. No necesitas hacer nada, ¡funciona solo!

### Agregar Productos Manualmente

Si quieres buscar productos ahora mismo:

1. **Desde línea de comandos**:
```bash
python manage.py scrape_products --count 10
```

2. **Para probar sin guardar**:
```bash
python manage.py scrape_products --dry-run
```

---

## 🎯 Casos de Uso Comunes

### 1. Encontrar Productos Rentables

**Objetivo**: Productos con buen precio y alta calificación

```
http://localhost:8000/api/products/?max_price=50&min_rating=4.0&max_shipping_days=20
```

### 2. Productos de Electrónicos Populares

**Objetivo**: Gadgets y electrónicos bien valorados

```
http://localhost:8000/api/products/?categories=Electronics&min_rating=4.2&keywords=smart,wireless
```

### 3. Productos de Envío Rápido

**Objetivo**: Productos que llegan rápido al cliente

```
http://localhost:8000/api/products/?max_shipping_days=10&min_rating=4.0
```

### 4. Productos de Bajo Costo

**Objetivo**: Productos baratos para márgenes altos

```
http://localhost:8000/api/products/?max_price=25&min_rating=3.5
```

---

## 🛠️ Solución de Problemas

### Problema: "No veo productos"

**Solución**:
1. Ejecuta el comando para agregar productos:
   ```bash
   python manage.py scrape_products --count 10
   ```
2. Verifica en: http://localhost:8000/api/products/

### Problema: "Las notificaciones no llegan"

**Solución**:
1. Verifica que los tokens/URLs estén correctos
2. Prueba las notificaciones:
   ```bash
   python manage.py manage_cron test
   ```

### Problema: "El sistema está lento"

**Solución**:
1. Verifica el health check: http://localhost:8000/health/
2. Reduce la cantidad de productos por scraping
3. Aumenta los intervalos de tiempo en las tareas automáticas

### Problema: "Productos duplicados"

**Solución**:
El sistema previene duplicados automáticamente por URL. Si ves duplicados:
1. Ejecuta el comando de limpieza:
   ```bash
   python manage.py shell
   >>> from products.services.product_manager import ProductManager
   >>> ProductManager.deduplicate_products()
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

1. **Datos Mock**: Actualmente usa datos de prueba. En producción se conectaría a APIs reales

2. **Scraping Manual**: Para obtener datos reales de AliExpress necesitarías configuración adicional

3. **Sin Interfaz Gráfica**: Actualmente es solo API. Se puede agregar una interfaz web posteriormente

---

## 📞 Soporte

### Si necesitas ayuda:

1. **Health Check**: Siempre revisa primero http://localhost:8000/health/
2. **Logs**: Revisa el archivo `dropship_bot.log`
3. **Tests**: Ejecuta `python manage.py test products` para verificar que todo funcione
4. **Documentación Técnica**: Consulta el manual técnico para configuraciones avanzadas

### Información de contacto:
- 📧 Email: [tu-email@ejemplo.com]
- 💬 Chat: [tu-canal-de-soporte]
- 📖 Documentación: README.md

---

**¡Feliz dropshipping! 🚀**