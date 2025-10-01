#!/usr/bin/env python
"""
Script interactivo para configurar notificaciones
Ayuda a configurar Discord y Telegram paso a paso
"""
import os
import sys
import requests
import json
from datetime import datetime

def test_discord_webhook(webhook_url):
    """Probar webhook de Discord"""
    print(f"\n🔍 Probando webhook de Discord...")
    
    test_message = {
        "embeds": [{
            "title": "🎉 Test de Dropshipping Bot",
            "description": "¡Las notificaciones de Discord están funcionando!",
            "color": 0x00FF00,
            "fields": [
                {"name": "Estado", "value": "✅ Configuración exitosa", "inline": True},
                {"name": "Fecha", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "inline": True}
            ],
            "footer": {"text": "Dropshipping Assistant"}
        }]
    }
    
    try:
        response = requests.post(webhook_url, json=test_message, timeout=10)
        if response.status_code == 204:
            print("✅ Discord: Mensaje enviado correctamente")
            return True
        else:
            print(f"❌ Discord: Error {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Discord: Error de conexión - {e}")
        return False

def test_telegram_bot(bot_token, chat_id):
    """Probar bot de Telegram"""
    print(f"\n🔍 Probando bot de Telegram...")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    test_message = {
        "chat_id": chat_id,
        "text": "🎉 *Test de Dropshipping Bot*\n\n✅ Las notificaciones de Telegram están funcionando!\n\n🕒 " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=test_message, timeout=10)
        if response.status_code == 200:
            print("✅ Telegram: Mensaje enviado correctamente")
            return True
        else:
            print(f"❌ Telegram: Error {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Telegram: Error de conexión - {e}")
        return False

def get_telegram_updates(bot_token):
    """Obtener actualizaciones para encontrar chat_id"""
    print(f"\n🔍 Obteniendo actualizaciones de Telegram...")
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data['result']:
                print("📋 Chats encontrados:")
                for update in data['result'][-5:]:  # Últimas 5 actualizaciones
                    if 'message' in update:
                        chat = update['message']['chat']
                        print(f"  - Chat ID: {chat['id']}")
                        if 'username' in chat:
                            print(f"    Username: @{chat['username']}")
                        if 'first_name' in chat:
                            print(f"    Nombre: {chat['first_name']}")
                        print()
                return True
            else:
                print("ℹ️ No hay mensajes. Envía un mensaje a tu bot primero.")
                return False
        else:
            print(f"❌ Error obteniendo actualizaciones: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def update_env_file(discord_url, telegram_token, telegram_chat_id):
    """Actualizar archivo .env con las configuraciones"""
    print(f"\n📝 Actualizando archivo .env...")
    
    # Leer archivo .env actual
    env_content = ""
    if os.path.exists('.env'):
        with open('.env', 'r', encoding='utf-8') as f:
            env_content = f.read()
    
    # Actualizar variables
    lines = env_content.split('\n')
    updated_lines = []
    
    discord_updated = False
    telegram_token_updated = False
    telegram_chat_updated = False
    
    for line in lines:
        if line.startswith('DISCORD_WEBHOOK_URL='):
            updated_lines.append(f'DISCORD_WEBHOOK_URL={discord_url}')
            discord_updated = True
        elif line.startswith('TELEGRAM_BOT_TOKEN='):
            updated_lines.append(f'TELEGRAM_BOT_TOKEN={telegram_token}')
            telegram_token_updated = True
        elif line.startswith('TELEGRAM_CHAT_ID='):
            updated_lines.append(f'TELEGRAM_CHAT_ID={telegram_chat_id}')
            telegram_chat_updated = True
        else:
            updated_lines.append(line)
    
    # Agregar variables si no existían
    if not discord_updated:
        updated_lines.append(f'DISCORD_WEBHOOK_URL={discord_url}')
    if not telegram_token_updated:
        updated_lines.append(f'TELEGRAM_BOT_TOKEN={telegram_token}')
    if not telegram_chat_updated:
        updated_lines.append(f'TELEGRAM_CHAT_ID={telegram_chat_id}')
    
    # Escribir archivo actualizado
    with open('.env', 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Archivo .env actualizado")

def main():
    """Función principal interactiva"""
    print("🔧 === CONFIGURADOR DE NOTIFICACIONES ===")
    print("Dropshipping Assistant - Configuración de Discord y Telegram")
    print("=" * 60)
    
    # Configurar Discord
    print("\n📱 CONFIGURACIÓN DE DISCORD")
    print("=" * 30)
    print("1. Ve a tu servidor de Discord")
    print("2. Haz clic derecho en un canal → Editar Canal")
    print("3. Ve a Integraciones → Webhooks → Crear Webhook")
    print("4. Copia la URL del webhook")
    print()
    
    discord_url = input("Pega tu URL de Discord webhook: ").strip()
    
    if discord_url:
        if test_discord_webhook(discord_url):
            print("✅ Discord configurado correctamente")
        else:
            print("❌ Error configurando Discord. Verifica la URL.")
            return
    else:
        print("⏭️ Saltando configuración de Discord")
        discord_url = ""
    
    # Configurar Telegram
    print("\n📲 CONFIGURACIÓN DE TELEGRAM")
    print("=" * 30)
    print("1. Busca @BotFather en Telegram")
    print("2. Envía /newbot y sigue las instrucciones")
    print("3. Copia el token que te da")
    print("4. Envía un mensaje a tu bot")
    print()
    
    telegram_token = input("Pega tu token de Telegram: ").strip()
    
    if telegram_token:
        # Obtener chat ID
        print("\n🔍 Para obtener tu Chat ID:")
        print("1. Envía un mensaje a tu bot")
        print("2. Presiona Enter para buscar tu chat")
        input("Presiona Enter cuando hayas enviado un mensaje...")
        
        if get_telegram_updates(telegram_token):
            telegram_chat_id = input("Ingresa tu Chat ID: ").strip()
            
            if telegram_chat_id:
                if test_telegram_bot(telegram_token, telegram_chat_id):
                    print("✅ Telegram configurado correctamente")
                else:
                    print("❌ Error configurando Telegram. Verifica token y chat ID.")
                    return
            else:
                print("⏭️ Saltando configuración de Telegram")
                telegram_token = ""
                telegram_chat_id = ""
        else:
            print("❌ No se pudo obtener información de Telegram")
            return
    else:
        print("⏭️ Saltando configuración de Telegram")
        telegram_token = ""
        telegram_chat_id = ""
    
    # Actualizar .env
    if discord_url or telegram_token:
        update_env_file(discord_url, telegram_token, telegram_chat_id)
        
        print("\n🎉 ¡CONFIGURACIÓN COMPLETADA!")
        print("=" * 40)
        print("✅ Las notificaciones están configuradas")
        print("📝 El archivo .env ha sido actualizado")
        print("🚀 Puedes probar el scraping para ver las notificaciones:")
        print("   python manage.py scrape_products")
    else:
        print("\n⚠️ No se configuraron notificaciones")

if __name__ == "__main__":
    main()