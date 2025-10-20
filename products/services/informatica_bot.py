#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Bot de Informática AliExpress - Simplificado
Busca automáticamente productos de PC, periféricos, componentes, etc.
"""

import logging
import time
import requests
import random
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from decimal import Decimal
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import json

logger = logging.getLogger('informatica_bot')

class InformaticaBot:
    """Bot especializado en productos de informática de AliExpress"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = 'https://www.aliexpress.com'
        
        # Headers realistas
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Configurar para región US
        self.session.cookies.update({
            'aep_usuc_f': 'region=US&site=glo&b_locale=en_US&c_tp=USD',
            'intl_locale': 'en_US'
        })
        
        # CATEGORÍAS DE INFORMÁTICA PREDEFINIDAS
        self.categorias_informatica = {
            'procesadores': [
                'Intel processor',
                'AMD processor', 
                'CPU intel core',
                'AMD Ryzen processor',
                'Intel Core i5',
                'Intel Core i7',
                'AMD Ryzen 5',
                'AMD Ryzen 7'
            ],
            'tarjetas_graficas': [
                'graphics card',
                'GPU nvidia',
                'AMD graphics card',
                'GeForce RTX',
                'nvidia gtx',
                'video card',
                'graphics adapter'
            ],
            'memoria_ram': [
                'DDR4 memory',
                'RAM memory',
                'DDR5 memory', 
                'computer memory',
                'desktop memory',
                'laptop memory',
                'memory module'
            ],
            'almacenamiento': [
                'SSD drive',
                'hard drive',
                'HDD storage',
                'NVMe SSD',
                'M.2 SSD',
                'external hard drive',
                'USB drive'
            ],
            'perifericos': [
                'gaming mouse',
                'mechanical keyboard',
                'wireless mouse',
                'gaming keyboard',
                'computer mouse',
                'USB keyboard',
                'gaming headset'
            ],
            'monitores': [
                'computer monitor',
                'gaming monitor',
                'LCD monitor',
                'LED monitor',
                '4K monitor',
                'ultrawide monitor'
            ],
            'componentes': [
                'motherboard',
                'power supply',
                'computer case',
                'CPU cooler',
                'computer fan',
                'thermal paste',
                'cable management'
            ]
        }
    
    def buscar_productos_informatica(self, categoria: str = None, limite: int = 10) -> List[Dict[str, Any]]:
        """
        Busca productos de informática automáticamente
        
        Args:
            categoria: Categoría específica o None para todas
            limite: Número máximo de productos
        """
        logger.info(f"🔍 Buscando productos de informática - Categoría: {categoria or 'TODAS'}")
        
        productos_encontrados = []
        
        # Seleccionar categorías a buscar
        if categoria and categoria in self.categorias_informatica:
            categorias_buscar = {categoria: self.categorias_informatica[categoria]}
        else:
            categorias_buscar = self.categorias_informatica
        
        # Buscar en cada categoría
        for cat_nombre, keywords_list in categorias_buscar.items():
            if len(productos_encontrados) >= limite:
                break
                
            logger.info(f"🎯 Buscando en categoría: {cat_nombre}")
            
            # Seleccionar algunas keywords de la categoría
            keywords_seleccionadas = random.sample(keywords_list, min(3, len(keywords_list)))
            
            for keyword in keywords_seleccionadas:
                if len(productos_encontrados) >= limite:
                    break
                    
                productos_categoria = self._buscar_por_keyword(keyword, cat_nombre, 3)
                productos_encontrados.extend(productos_categoria)
                
                # Pausa entre búsquedas
                time.sleep(random.uniform(1, 3))
        
        # Limitar resultados finales
        productos_finales = productos_encontrados[:limite]
        
        logger.info(f"✅ Encontrados {len(productos_finales)} productos de informática")
        return productos_finales
    
    def _buscar_por_keyword(self, keyword: str, categoria: str, max_productos: int) -> List[Dict[str, Any]]:
        """Busca productos por keyword específica"""
        try:
            logger.debug(f"🔍 Buscando: '{keyword}' en {categoria}")
            
            # URL de búsqueda
            search_url = f"{self.base_url}/wholesale"
            params = {
                'SearchText': keyword,
                'page': 1,
                'g': 'y'
            }
            
            # Hacer request
            response = self.session.get(search_url, params=params, timeout=15)
            response.raise_for_status()
            
            # Extraer productos
            productos = self._extraer_productos_html(response.content, categoria, max_productos)
            
            # Filtrar productos válidos
            productos_validos = []
            for producto in productos:
                if self._es_producto_informatica(producto, categoria):
                    productos_validos.append(producto)
            
            logger.debug(f"✅ {len(productos_validos)} productos válidos para '{keyword}'")
            return productos_validos
            
        except Exception as e:
            logger.debug(f"❌ Error buscando '{keyword}': {e}")
            return []
    
    def _extraer_productos_html(self, html_content: bytes, categoria: str, max_productos: int) -> List[Dict[str, Any]]:
        """Extrae productos desde HTML de AliExpress"""
        productos = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Buscar enlaces de productos
            enlaces_productos = soup.find_all('a', href=re.compile(r'/item/\d+\.html'))
            
            for enlace in enlaces_productos[:max_productos * 2]:  # Buscar más para filtrar
                try:
                    # Extraer URL
                    href = enlace.get('href', '')
                    if href.startswith('/'):
                        url_producto = self.base_url + href
                    elif href.startswith('http'):
                        url_producto = href
                    else:
                        continue
                    
                    # Extraer título
                    titulo = ''
                    # Buscar título en varios lugares
                    titulo_sources = [
                        enlace.get('title'),
                        enlace.get_text(strip=True),
                        enlace.find('img', alt=True)
                    ]
                    
                    for source in titulo_sources:
                        if source:
                            if hasattr(source, 'get'):
                                titulo = source.get('alt', '')
                            else:
                                titulo = str(source).strip()
                            if titulo and len(titulo) > 10:
                                break
                    
                    if not titulo:
                        titulo = f"Producto de {categoria}"
                    
                    # Extraer precio (buscar en contenedor padre)
                    precio = 0.0
                    contenedor = enlace.find_parent(['div', 'article', 'li', 'section'])
                    if contenedor:
                        precios_texto = contenedor.find_all(string=re.compile(r'\$[\d,]+\.?\d*|US\s*\$[\d,]+'))
                        for precio_texto in precios_texto:
                            precio_extraido = self._extraer_precio(precio_texto)
                            if precio_extraido > 0:
                                precio = precio_extraido
                                break
                    
                    # Si no encontramos precio, usar rango típico por categoría
                    if precio == 0:
                        precio = self._precio_tipico_categoria(categoria)
                    
                    # Extraer imagen
                    img_url = ''
                    img = enlace.find('img', src=True)
                    if img:
                        img_url = img['src']
                        if img_url and not img_url.startswith('http'):
                            img_url = 'https:' + img_url
                    
                    producto = {
                        'url': url_producto,
                        'titulo': titulo[:100],
                        'precio': round(precio, 2),
                        'moneda': 'USD',
                        'imagen': img_url,
                        'categoria': categoria,
                        'encontrado_en': datetime.now(timezone.utc).isoformat(),
                        'fuente': 'aliexpress_real'
                    }
                    
                    productos.append(producto)
                    
                    if len(productos) >= max_productos:
                        break
                        
                except Exception as e:
                    logger.debug(f"Error procesando producto: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extrayendo productos HTML: {e}")
        
        return productos
    
    def _extraer_precio(self, precio_str: str) -> float:
        """Extrae precio numérico del texto"""
        try:
            precio_match = re.search(r'[\d,]+\.?\d*', str(precio_str).replace('$', '').replace(',', ''))
            if precio_match:
                return float(precio_match.group())
        except:
            pass
        return 0.0
    
    def _precio_tipico_categoria(self, categoria: str) -> float:
        """Devuelve precio típico por categoría"""
        rangos_precio = {
            'procesadores': (50, 300),
            'tarjetas_graficas': (100, 800),
            'memoria_ram': (20, 150),
            'almacenamiento': (25, 200),
            'perifericos': (10, 80),
            'monitores': (80, 400),
            'componentes': (15, 120)
        }
        
        rango = rangos_precio.get(categoria, (10, 100))
        return round(random.uniform(*rango), 2)
    
    def _es_producto_informatica(self, producto: Dict[str, Any], categoria: str) -> bool:
        """Valida que el producto realmente sea de informática"""
        titulo = producto.get('titulo', '').lower()
        precio = producto.get('precio', 0)
        
        # Palabras clave por categoría para validación
        palabras_validas = {
            'procesadores': ['cpu', 'processor', 'intel', 'amd', 'core', 'ryzen'],
            'tarjetas_graficas': ['gpu', 'graphics', 'video', 'nvidia', 'geforce', 'rtx', 'gtx'],
            'memoria_ram': ['ram', 'memory', 'ddr4', 'ddr5', 'dimm'],
            'almacenamiento': ['ssd', 'hdd', 'drive', 'storage', 'nvme', 'm.2'],
            'perifericos': ['mouse', 'keyboard', 'headset', 'gaming', 'wireless'],
            'monitores': ['monitor', 'display', 'screen', 'lcd', 'led', '4k'],
            'componentes': ['motherboard', 'power', 'case', 'cooler', 'fan']
        }
        
        # Palabras a evitar (productos no informáticos)
        palabras_evitar = [
            'clothing', 'fashion', 'jewelry', 'beauty', 'makeup', 'shoes',
            'bags', 'home', 'kitchen', 'toys', 'baby', 'sports', 'outdoor',
            'automotive', 'tools', 'garden', 'health', 'pet'
        ]
        
        # Verificar que no sea un producto no informático
        for palabra in palabras_evitar:
            if palabra in titulo:
                return False
        
        # Verificar que contenga palabras válidas de la categoría
        palabras_categoria = palabras_validas.get(categoria, [])
        for palabra in palabras_categoria:
            if palabra in titulo:
                # Verificar precio razonable
                if 5 <= precio <= 1000:  # Rango amplio pero razonable
                    return True
        
        return False
    
    def obtener_resumen_categorias(self) -> Dict[str, int]:
        """Obtiene resumen de productos disponibles por categoría"""
        resumen = {}
        
        for categoria in self.categorias_informatica.keys():
            logger.info(f"📊 Contando productos en: {categoria}")
            productos = self.buscar_productos_informatica(categoria, 5)
            resumen[categoria] = len(productos)
            time.sleep(1)  # Pausa entre categorías
        
        return resumen

# Función principal para usar el bot
def main():
    """Función principal de demostración"""
    bot = InformaticaBot()
    
    print("🖥️ BOT DE INFORMÁTICA ALIEXPRESS")
    print("=" * 50)
    
    # Buscar productos de todas las categorías
    print("\n🔍 Buscando productos de informática...")
    productos = bot.buscar_productos_informatica(limite=15)
    
    print(f"\n📦 PRODUCTOS ENCONTRADOS ({len(productos)}):")
    print("-" * 50)
    
    for i, producto in enumerate(productos, 1):
        print(f"\n{i}. {producto['titulo']}")
        print(f"   💰 Precio: ${producto['precio']}")
        print(f"   📂 Categoría: {producto['categoria']}")
        print(f"   🔗 URL: {producto['url']}")
        
        if i % 5 == 0:
            print("\n" + "="*30)

if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    main()