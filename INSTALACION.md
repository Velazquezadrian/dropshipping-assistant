# 🚀 Guía de Instalación Rápida - Dropship Bot

## Instalación en 5 Minutos

### ✅ Prerrequisitos

- Python 3.8 o superior
- Git (opcional)
- 2GB de RAM disponible
- 1GB de espacio en disco

### 📥 Paso 1: Obtener el Código

```bash
# Si tienes Git
git clone [tu-repositorio]
cd Dropshiping

# Si descargaste un ZIP
# Descomprimir y entrar a la carpeta
cd Dropshiping
```

### 🐍 Paso 2: Configurar Python

#### Windows:
```powershell
# Crear entorno virtual
python -m venv .venv

# Activar entorno
.venv\Scripts\activate

# Verificar activación (debería mostrar (.venv) al inicio)
```

#### Linux/macOS:
```bash
# Crear entorno virtual
python3 -m venv .venv

# Activar entorno
source .venv/bin/activate

# Verificar activación (debería mostrar (.venv) al inicio)
```

### 📦 Paso 3: Instalar Dependencias

```bash
# Instalar todas las dependencias
pip install django djangorestframework django-crontab django-filter requests python-telegram-bot

# O usando el archivo requirements.txt
pip install -r requirements.txt
```

### 🗄️ Paso 4: Configurar Base de Datos

```bash
# Crear base de datos (SQLite)
python manage.py migrate

# ¡Listo! La base de datos está configurada
```

### 🚀 Paso 5: Ejecutar el Sistema

```bash
# Iniciar servidor
python manage.py runserver

# ¡El sistema estará disponible en http://localhost:8000!
```

### ✅ Paso 6: Verificar Instalación

1. **Abrir navegador**: Ve a http://localhost:8000/health/
2. **Deberías ver**:
   ```json
   {
       "status": "ok",
       "message": "Dropship Bot API está funcionando"
   }
   ```

### 🛍️ Paso 7: Agregar Productos de Prueba

```bash
# En una nueva terminal (manteniendo el servidor corriendo)
# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Agregar productos de prueba
python manage.py scrape_products --platform mock --count 10
```

### 🎯 Paso 8: Probar la API

- **Ver productos**: http://localhost:8000/api/products/
- **Ver estadísticas**: http://localhost:8000/api/products/stats/
- **Filtrar productos**: http://localhost:8000/api/products/?max_price=50

---

## 🔧 Configuración Opcional

### 🤖 Configurar Notificaciones Telegram

1. **Crear bot**: Habla con @BotFather en Telegram
2. **Obtener token**: Guarda el token que te dé
3. **Obtener chat ID**: Envía mensaje a tu bot, luego ve a:
   ```
   https://api.telegram.org/bot<TU_TOKEN>/getUpdates
   ```
4. **Configurar**: Edita `dropship_bot/settings.py`:
   ```python
   TELEGRAM_BOT_TOKEN = 'tu_token_aqui'
   TELEGRAM_CHAT_ID = 'tu_chat_id_aqui'
   ```

### 🎮 Configurar Notificaciones Discord

1. **Crear webhook**: En tu servidor Discord → Configuración → Integraciones → Webhooks
2. **Copiar URL**: Guarda la URL del webhook
3. **Configurar**: Edita `dropship_bot/settings.py`:
   ```python
   DISCORD_WEBHOOK_URL = 'tu_webhook_url_aqui'
   ```

---

## 🎮 Comandos Útiles

### Gestión de Productos
```bash
# Agregar más productos
python manage.py scrape_products --count 20

# Solo ver qué productos agregaría (no guarda)
python manage.py scrape_products --dry-run

# Agregar de plataforma específica
python manage.py scrape_products --platform mock --count 5
```

### Tests y Verificación
```bash
# Ejecutar todos los tests
python manage.py test products

# Verificar que todo funcione
python manage.py manage_cron test
```

### Administración (Opcional)
```bash
# Crear usuario administrador
python manage.py createsuperuser

# Luego ir a http://localhost:8000/admin/
```

---

## 📱 Usar la API

### Ejemplos Básicos

#### Ver todos los productos:
```
GET http://localhost:8000/api/products/
```

#### Filtrar productos baratos:
```
GET http://localhost:8000/api/products/?max_price=30
```

#### Buscar productos específicos:
```
GET http://localhost:8000/api/products/?search=smartphone
```

#### Ver estadísticas:
```
GET http://localhost:8000/api/products/stats/
```

---

## 🆘 Solución de Problemas

### ❌ Error: "Python no encontrado"
**Solución**: Instala Python desde https://python.org

### ❌ Error: "pip no encontrado"
**Solución**: 
```bash
# Windows
python -m ensurepip --upgrade

# Linux
sudo apt install python3-pip
```

### ❌ Error: "Puerto 8000 en uso"
**Solución**:
```bash
# Usar otro puerto
python manage.py runserver 8001

# O encontrar qué usa el puerto 8000
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/macOS
```

### ❌ Error: "No veo productos"
**Solución**:
```bash
# Agregar productos de prueba
python manage.py scrape_products --count 10
```

### ❌ El servidor se detiene solo
**Solución**:
```bash
# Revisar errores
python manage.py check

# Ver logs
cat dropship_bot.log  # Linux/macOS
type dropship_bot.log # Windows
```

---

## 📞 ¿Necesitas Ayuda?

1. **Health Check**: Siempre revisa http://localhost:8000/health/ primero
2. **Tests**: Ejecuta `python manage.py test products` para verificar
3. **Logs**: Revisa el archivo `dropship_bot.log`
4. **Manual Completo**: Lee `MANUAL_USUARIO.md` para más detalles
5. **Manual Técnico**: Lee `MANUAL_TECNICO.md` para configuraciones avanzadas

---

## 🎉 ¡Listo!

Tu sistema Dropship Bot está funcionando. Ahora puedes:

- ✅ Ver productos en http://localhost:8000/api/products/
- ✅ Filtrar y buscar productos
- ✅ Ver estadísticas en tiempo real
- ✅ Recibir notificaciones automáticas
- ✅ Agregar nuevos productos automáticamente

**¡Feliz dropshipping! 🚀**