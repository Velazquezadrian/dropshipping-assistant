# 🔐 Configuración de Certificados SSL

## Para desarrollo (certificados auto-firmados)

### 1. Con OpenSSL (Linux/Mac o Windows con OpenSSL):

```bash
# Crear certificado auto-firmado
cd certs
openssl req -x509 -newkey rsa:4096 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Crear parámetros Diffie-Hellman
openssl dhparam -out dhparam.pem 2048
```

### 2. Con PowerShell (Windows):

```powershell
# Crear certificado auto-firmado para localhost
$cert = New-SelfSignedCertificate -DnsName "localhost", "127.0.0.1" -CertStoreLocation "cert:\LocalMachine\My" -NotAfter (Get-Date).AddYears(1)

# Exportar certificado
$password = ConvertTo-SecureString -String "password123" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath ".\certs\nginx-selfsigned.pfx" -Password $password

# Exportar clave pública
Export-Certificate -Cert $cert -FilePath ".\certs\nginx-selfsigned.crt"
```

## Para producción (Let's Encrypt)

### 1. Instalar Certbot:

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

### 2. Obtener certificado:

```bash
# Obtener certificado para tu dominio
sudo certbot --nginx -d tu-dominio.com -d www.tu-dominio.com

# O manualmente
sudo certbot certonly --webroot -w /var/www/html -d tu-dominio.com
```

### 3. Configurar renovación automática:

```bash
# Agregar al crontab
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Configuración de archivos

Los certificados deben estar en:
- `certs/nginx-selfsigned.crt` - Certificado público
- `certs/nginx-selfsigned.key` - Clave privada
- `certs/dhparam.pem` - Parámetros DH (opcional)

## Variables de entorno para producción

Agregar al archivo `.env`:

```env
# Certificados SSL
SSL_CERTIFICATE_PATH=/app/certs/nginx-selfsigned.crt
SSL_CERTIFICATE_KEY_PATH=/app/certs/nginx-selfsigned.key
SSL_DHPARAM_PATH=/app/certs/dhparam.pem

# Configuración HTTPS
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Scripts de automatización

### Script de renovación (Linux):
```bash
#!/bin/bash
# Archivo: renew_certificates.sh

echo "Renovando certificados SSL..."
certbot renew --quiet

if [ $? -eq 0 ]; then
    echo "Certificados renovados exitosamente"
    docker-compose restart nginx
else
    echo "Error al renovar certificados"
fi
```

### Script de monitoreo de certificados:
```bash
#!/bin/bash
# Verificar expiración de certificados

CERT_FILE="/app/certs/nginx-selfsigned.crt"
DAYS_BEFORE_EXPIRY=30

if [ -f "$CERT_FILE" ]; then
    EXPIRY_DATE=$(openssl x509 -in "$CERT_FILE" -noout -enddate | cut -d= -f2)
    EXPIRY_EPOCH=$(date -d "$EXPIRY_DATE" +%s)
    CURRENT_EPOCH=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( ($EXPIRY_EPOCH - $CURRENT_EPOCH) / 86400 ))
    
    if [ $DAYS_UNTIL_EXPIRY -lt $DAYS_BEFORE_EXPIRY ]; then
        echo "⚠️ ALERTA: Certificado expira en $DAYS_UNTIL_EXPIRY días"
        # Enviar notificación
    else
        echo "✅ Certificado válido por $DAYS_UNTIL_EXPIRY días"
    fi
else
    echo "❌ Archivo de certificado no encontrado"
fi
```