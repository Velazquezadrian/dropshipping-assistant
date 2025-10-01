#!/usr/bin/env python3
"""
🔐 Configurador de SSL para Producción
Configura certificados SSL para el sistema de dropshipping
"""

import os
import subprocess
import sys
from pathlib import Path

def generate_self_signed_cert():
    """Generar certificado auto-firmado para desarrollo/testing"""
    print("🔐 Generando certificado SSL auto-firmado...")
    
    # Crear directorio de certificados
    cert_dir = Path("certs")
    cert_dir.mkdir(exist_ok=True)
    
    # Configuración del certificado
    cert_file = cert_dir / "nginx-selfsigned.crt"
    key_file = cert_dir / "nginx-selfsigned.key"
    
    # Comando para generar certificado
    cmd = [
        "openssl", "req", "-x509", "-nodes",
        "-days", "365",
        "-newkey", "rsa:2048",
        "-keyout", str(key_file),
        "-out", str(cert_file),
        "-subj", "/C=US/ST=State/L=City/O=Organization/CN=localhost"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Certificado generado: {cert_file}")
        print(f"✅ Clave privada generada: {key_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error generando certificado: {e}")
        return False
    except FileNotFoundError:
        print("❌ OpenSSL no encontrado. Instala OpenSSL primero.")
        print("   Windows: https://slproweb.com/products/Win32OpenSSL.html")
        return False

def setup_letsencrypt():
    """Configurar Let's Encrypt para certificados reales"""
    print("🔐 Configurando Let's Encrypt...")
    
    domain = input("Ingresa tu dominio (ej: tu-sitio.com): ").strip()
    email = input("Ingresa tu email para Let's Encrypt: ").strip()
    
    if not domain or not email:
        print("❌ Dominio y email son requeridos")
        return False
    
    print(f"""
📋 Configuración Let's Encrypt:
   Dominio: {domain}
   Email: {email}
   
⚠️ IMPORTANTE: 
1. Tu dominio debe apuntar a esta IP
2. Los puertos 80 y 443 deben estar abiertos
3. El servidor debe estar accesible desde internet

Para continuar con Let's Encrypt, ejecuta estos comandos:

# 1. Instalar Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 2. Obtener certificado
sudo certbot --nginx -d {domain} --email {email} --agree-tos --non-interactive

# 3. Configurar renovación automática
sudo crontab -e
# Agregar línea: 0 12 * * * /usr/bin/certbot renew --quiet

Los certificados se instalarán automáticamente en:
/etc/letsencrypt/live/{domain}/fullchain.pem
/etc/letsencrypt/live/{domain}/privkey.pem
""")
    
    return True

def create_ssl_config():
    """Crear configuración SSL para nginx"""
    ssl_config = """
# 🔐 Configuración SSL Optimizada para Nginx

# Configuración SSL moderna
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES128-SHA256:ECDHE-RSA-AES256-SHA384:ECDHE-RSA-AES128-SHA:ECDHE-RSA-AES256-SHA:DHE-RSA-AES128-SHA256:DHE-RSA-AES256-SHA256:AES128-GCM-SHA256:AES256-GCM-SHA384:AES128-SHA256:AES256-SHA256:AES128-SHA:AES256-SHA:DES-CBC3-SHA;
ssl_prefer_server_ciphers off;

# Configuración de sesión SSL
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
ssl_session_tickets off;

# HSTS (HTTP Strict Transport Security)
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

# Otros headers de seguridad
add_header X-Frame-Options DENY always;
add_header X-Content-Type-Options nosniff always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;

# OCSP Stapling
ssl_stapling on;
ssl_stapling_verify on;
resolver 8.8.8.8 8.8.4.4 valid=300s;
resolver_timeout 5s;
"""
    
    # Crear archivo de configuración SSL
    with open("certs/ssl_config.conf", "w") as f:
        f.write(ssl_config)
    
    print("✅ Configuración SSL creada en certs/ssl_config.conf")
    return True

def main():
    """Función principal"""
    print("🔐 CONFIGURADOR DE SSL PARA PRODUCCIÓN")
    print("=" * 50)
    
    print("\nOpciones disponibles:")
    print("1. Generar certificado auto-firmado (para testing)")
    print("2. Configurar Let's Encrypt (para producción)")
    print("3. Crear configuración SSL optimizada")
    print("4. Todo lo anterior")
    
    choice = input("\nSelecciona una opción (1-4): ").strip()
    
    if choice == "1":
        generate_self_signed_cert()
    elif choice == "2":
        setup_letsencrypt()
    elif choice == "3":
        create_ssl_config()
    elif choice == "4":
        print("\n🚀 Configuración completa de SSL...")
        generate_self_signed_cert()
        create_ssl_config()
        print("\n📋 Certificados auto-firmados creados para testing")
        print("Para producción, configura Let's Encrypt manualmente")
        setup_letsencrypt()
    else:
        print("❌ Opción no válida")
        return False
    
    print("\n🎉 Configuración SSL completada!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)