#!/usr/bin/env python
"""
Script para obtener Chat ID de Telegram
"""
import requests

def get_telegram_chat_id(bot_token):
    """Obtener Chat ID de Telegram"""
    print(f"🔍 Obteniendo información de tu bot de Telegram...")
    
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa con el bot")
            
            if data['result']:
                print("📋 Mensajes encontrados:")
                for update in data['result'][-5:]:  # Últimas 5 actualizaciones
                    if 'message' in update:
                        chat = update['message']['chat']
                        message = update['message']
                        print(f"  📱 Chat ID: {chat['id']}")
                        if 'username' in chat:
                            print(f"     Username: @{chat['username']}")
                        if 'first_name' in chat:
                            print(f"     Nombre: {chat['first_name']}")
                        print(f"     Mensaje: {message.get('text', 'N/A')}")
                        print(f"     Fecha: {message.get('date', 'N/A')}")
                        print()
                
                # Obtener el chat ID más reciente
                if data['result']:
                    latest_chat_id = data['result'][-1]['message']['chat']['id']
                    print(f"🎯 Chat ID más reciente: {latest_chat_id}")
                    return latest_chat_id
            else:
                print("ℹ️ No hay mensajes. Envía un mensaje a tu bot primero.")
                print(f"📱 Busca tu bot en Telegram y envía '/start' o cualquier mensaje")
                return None
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_telegram_message(bot_token, chat_id):
    """Enviar mensaje de prueba"""
    print(f"🧪 Enviando mensaje de prueba...")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    
    message = {
        "chat_id": chat_id,
        "text": "🎉 *¡Telegram configurado correctamente!*\n\n✅ Tu bot de Dropshipping está funcionando\n🕒 " + str(datetime.now()),
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=message, timeout=10)
        if response.status_code == 200:
            print("✅ Mensaje enviado correctamente")
            return True
        else:
            print(f"❌ Error enviando mensaje: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    from datetime import datetime
    
    bot_token = "8426879269:AAFiOdQvZEuBWjh3CQOalbCI1JZaIobRhtM"
    
    print("🤖 === CONFIGURADOR DE TELEGRAM ===")
    print("1. Asegúrate de haber enviado un mensaje a tu bot")
    print("2. El bot debe estar activo")
    print()
    
    chat_id = get_telegram_chat_id(bot_token)
    
    if chat_id:
        print(f"\n✅ Chat ID encontrado: {chat_id}")
        
        # Probar envío de mensaje
        if test_telegram_message(bot_token, chat_id):
            print(f"\n🎉 ¡Telegram configurado exitosamente!")
            print(f"📝 Agrega esto a tu archivo .env:")
            print(f"TELEGRAM_CHAT_ID={chat_id}")
        else:
            print(f"\n❌ Error enviando mensaje de prueba")
    else:
        print(f"\n⚠️ No se encontró Chat ID")
        print(f"📱 Envía un mensaje a tu bot primero y vuelve a ejecutar este script")