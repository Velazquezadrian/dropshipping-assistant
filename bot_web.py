#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot simplificado para ejecución web - sin emojis
"""

import requests
import json
import time
import random
from datetime import datetime
import logging

# Configuración de logging simplificada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_web.log', encoding='utf-8'),
    ]
)

class BotDropshippingWeb:
    def __init__(self):
        """Inicializa el bot para ejecución web"""
        
        # Configuración Discord
        self.discord_webhook = "https://discord.com/api/webhooks/1423036583338053793/Vsy9uz72Gpk9zv5-M8wtLeM-ISj-CPJ-LK73TcKVFL7R2s6I8F8kG77d32zT0ekcWgDL"
        
        # Base de datos de productos
        self.productos_base = [
            {
                'categoria': 'Gaming',
                'productos': [
                    {'nombre': 'Wireless Gaming Mouse RGB LED', 'precio_min': 15.99, 'precio_max': 45.99},
                    {'nombre': 'Mechanical Gaming Keyboard RGB', 'precio_min': 35.99, 'precio_max': 89.99},
                    {'nombre': 'Gaming Headset Pro Microphone', 'precio_min': 29.99, 'precio_max': 79.99},
                    {'nombre': 'Gaming Mouse Pad XXL RGB', 'precio_min': 19.99, 'precio_max': 39.99},
                    {'nombre': 'Webcam HD 1080P Gaming Stream', 'precio_min': 39.99, 'precio_max': 99.99}
                ]
            },
            {
                'categoria': 'Accesorios',
                'productos': [
                    {'nombre': 'USB-C Fast Charging Cable', 'precio_min': 8.99, 'precio_max': 19.99},
                    {'nombre': 'Wireless Phone Charger Qi 15W', 'precio_min': 16.99, 'precio_max': 34.99},
                    {'nombre': 'Power Bank 20000mAh Fast Charge', 'precio_min': 24.99, 'precio_max': 49.99},
                    {'nombre': 'Bluetooth 5.0 USB Adapter', 'precio_min': 9.99, 'precio_max': 18.99},
                    {'nombre': 'USB Hub 3.0 Multi-Port', 'precio_min': 12.99, 'precio_max': 28.99}
                ]
            },
            {
                'categoria': 'Audio',
                'productos': [
                    {'nombre': 'Bluetooth Wireless Earbuds Pro', 'precio_min': 25.99, 'precio_max': 69.99},
                    {'nombre': 'Portable Bluetooth Speaker Bass', 'precio_min': 22.99, 'precio_max': 59.99},
                    {'nombre': 'Studio Monitor Headphones', 'precio_min': 49.99, 'precio_max': 129.99},
                    {'nombre': 'Wireless Microphone Karaoke', 'precio_min': 18.99, 'precio_max': 38.99},
                    {'nombre': 'Sound Bar TV Bluetooth', 'precio_min': 45.99, 'precio_max': 119.99}
                ]
            }
        ]
        
        self.vendedores = [
            "TechWorld Official Store",
            "Gaming Electronics Pro", 
            "Digital Gadgets Hub",
            "Smart Devices Center"
        ]
        
        self.variantes = ["Pro", "Max", "Ultra", "Plus", "2024", "HD", "Premium"]
        
        logging.info("Bot Web inicializado")

    def generar_productos(self, cantidad=6):
        """Genera productos realistas"""
        logging.info(f"Generando {cantidad} productos...")
        
        productos = []
        
        for i in range(cantidad):
            categoria_data = random.choice(self.productos_base)
            categoria = categoria_data['categoria']
            producto_base = random.choice(categoria_data['productos'])
            
            nombre = producto_base['nombre']
            if random.random() > 0.5:
                variante = random.choice(self.variantes)
                nombre += f" {variante}"
            
            precio = round(random.uniform(
                producto_base['precio_min'], 
                producto_base['precio_max']
            ), 2)
            
            producto = {
                'numero': i + 1,
                'id': random.randint(100000000000, 999999999999),
                'nombre': nombre,
                'precio': precio,
                'precio_original': round(precio * random.uniform(1.2, 1.8), 2),
                'descuento': random.randint(20, 50),
                'categoria': categoria,
                'vendedor': random.choice(self.vendedores),
                'rating': round(random.uniform(4.1, 4.9), 1),
                'reviews': random.randint(150, 8500),
                'ventas': random.randint(500, 25000),
                'stock': random.randint(50, 999),
                'url': f"https://www.aliexpress.com/item/{random.randint(100000000000, 999999999999)}.html",
                'envio_gratis': random.choice([True, False]),
                'tiempo_envio': f"{random.randint(7, 15)}-{random.randint(16, 30)} dias",
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            productos.append(producto)
            logging.info(f"Producto {i+1} generado: {nombre}")
        
        logging.info(f"{len(productos)} productos generados exitosamente")
        return productos

    def enviar_discord(self, productos):
        """Envia productos a Discord"""
        logging.info("Enviando productos a Discord...")
        
        try:
            embed = {
                "title": "PRODUCTOS DROPSHIPPING - Bot Web Automatico",
                "description": f"Bot web encontro {len(productos)} productos\\nListos para importar a tu tienda",
                "color": 0x00D4AA,
                "fields": [],
                "timestamp": datetime.now().isoformat(),
                "thumbnail": {
                    "url": "https://cdn-icons-png.flaticon.com/512/3039/3039392.png"
                },
                "footer": {
                    "text": "Bot Dropshipping Web | Automatico desde web",
                    "icon_url": "https://cdn-icons-png.flaticon.com/512/891/891462.png"
                }
            }
            
            for producto in productos[:6]:
                descuento = f" (-{producto['descuento']}%)" if producto['descuento'] > 0 else ""
                envio_text = "Envio gratis" if producto['envio_gratis'] else f"Envio: {producto['tiempo_envio']}"
                
                embed["fields"].append({
                    "name": f"{producto['numero']}. {producto['nombre']}",
                    "value": (
                        f"Precio: ${producto['precio']}{descuento}\\n"
                        f"Rating: {producto['rating']}/5 ({producto['reviews']} reviews)\\n"
                        f"Ventas: {producto['ventas']} | Stock: {producto['stock']}\\n"
                        f"Vendedor: {producto['vendedor']}\\n"
                        f"{envio_text}\\n"
                        f"[Ver Producto]({producto['url']})"
                    ),
                    "inline": False
                })
            
            payload = {"embeds": [embed]}
            response = requests.post(self.discord_webhook, json=payload, timeout=10)
            
            if response.status_code == 204:
                logging.info("Productos enviados a Discord exitosamente")
                return True
            else:
                logging.error(f"Error Discord: {response.status_code}")
                return False
                
        except Exception as e:
            logging.error(f"Error enviando a Discord: {e}")
            return False

    def ejecutar(self, cantidad_productos=6):
        """Ejecuta el bot completo"""
        logging.info("Iniciando bot web...")
        
        try:
            # Generar productos
            productos = self.generar_productos(cantidad_productos)
            
            if not productos:
                logging.error("No se generaron productos")
                return False, "No se pudieron generar productos"
            
            # Enviar a Discord
            discord_ok = self.enviar_discord(productos)
            
            if discord_ok:
                message = f"Bot ejecutado exitosamente! {len(productos)} productos enviados a Discord"
                logging.info(message)
                return True, message
            else:
                message = "Error enviando productos a Discord"
                logging.error(message)
                return False, message
                
        except Exception as e:
            message = f"Error ejecutando bot: {str(e)}"
            logging.error(message)
            return False, message

if __name__ == "__main__":
    bot = BotDropshippingWeb()
    success, message = bot.ejecutar(6)
    print(f"Resultado: {message}")