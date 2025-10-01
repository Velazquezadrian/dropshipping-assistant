# 🐳 Docker Configuration para Dropshipping Assistant

# Usa la imagen oficial de Python 3.13
FROM python:3.13-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorio para la base de datos
RUN mkdir -p /app/data

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 8000

# Variables de entorno por defecto
ENV DJANGO_SETTINGS_MODULE=dropship_bot.settings
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Comando por defecto
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Comando para producción (descomenta para usar con gunicorn)
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dropship_bot.wsgi:application"]