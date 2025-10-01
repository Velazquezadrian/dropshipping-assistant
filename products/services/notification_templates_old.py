"""
🎨 Sistema de Plantillas Personalizadas para Notificaciones
Plantillas dinámicas, formateo inteligente y estilos adaptativos
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from products.models import Product
from products.services.notification_filters import NotificationPriority

logger = logging.getLogger('notifications')


class TemplateType(Enum):
    """Tipos de plantillas disponibles"""
    TEXT = "text"
    MARKDOWN = "markdown"
    HTML = "html"
    RICH = "rich"  # Para Discord embeds


@dataclass
class NotificationTemplate:
    """Plantilla de notificación personalizable"""
    name: str
    template_type: TemplateType
    subject_template: str
    body_template: str
    priority_styles: Dict[str, Dict[str, Any]]
    platform_specific: Dict[str, Dict[str, Any]]
    variables: List[str]
    description: str = ""
    enabled: bool = True


class NotificationTemplateEngine:
    """Motor de plantillas para notificaciones"""
    
    def __init__(self):
        self.templates = self._load_default_templates()
        self.platform_limits = {
            'telegram': {'max_length': 4096, 'supports_markdown': True, 'supports_html': True},
            'discord': {'max_length': 2000, 'supports_markdown': True, 'supports_embeds': True}
        }
    
    def _load_default_templates(self) -> Dict[str, NotificationTemplate]:
        """Cargar plantillas por defecto"""
        templates = {}
        
        # Plantilla por defecto
        templates['default'] = NotificationTemplate(
            name="default",
            template_type=TemplateType.MARKDOWN,
            subject_template="🆕 Nuevo Producto Encontrado",
            body_template="""
**{title}**

💰 **Precio:** ${price}
⭐ **Rating:** {rating}/5.0 ({rating_emoji})
📦 **Categoría:** {category}
🚚 **Envío:** {shipping_time} días
🔗 **Plataforma:** {source_platform}

{description_short}

[Ver Producto]({url})

_{timestamp}_
            """.strip(),
            priority_styles={
                'low': {'emoji': '🟢', 'color': 0x00ff00},
                'normal': {'emoji': '🔵', 'color': 0x0099ff},
                'high': {'emoji': '🟡', 'color': 0xffaa00},
                'urgent': {'emoji': '🔴', 'color': 0xff0000}
            },
            platform_specific={
                'telegram': {'parse_mode': 'Markdown'},
                'discord': {'embed': True}
            },
            variables=['title', 'price', 'rating', 'category', 'shipping_time', 'source_platform', 'url'],
            description="Plantilla estándar para productos"
        )
        
        # Plantilla para productos de alta calidad
        templates['high_quality'] = NotificationTemplate(
            name="high_quality",
            template_type=TemplateType.MARKDOWN,
            subject_template="💎 Producto Premium Detectado",
            body_template="""
✨ **PRODUCTO PREMIUM** ✨

**{title}**

💎 **Precio Excelente:** ${price}
⭐ **Rating Superior:** {rating}/5.0 {rating_emoji}
🏆 **Categoría:** {category}
📦 **Envío Rápido:** {shipping_time} días
🌟 **Plataforma:** {source_platform}

**¿Por qué es especial?**
• Rating excepcional ({rating}/5.0)
• Precio competitivo
• Excelente relación calidad-precio

{description_short}

🛒 [¡Conseguir Ahora!]({url})

_{timestamp}_
            """.strip(),
            priority_styles={
                'low': {'emoji': '💎', 'color': 0x00ff88},
                'normal': {'emoji': '💎', 'color': 0x00aaff},
                'high': {'emoji': '💎', 'color': 0xffaa00},
                'urgent': {'emoji': '💎', 'color': 0xff4400}
            },
            platform_specific={
                'telegram': {'parse_mode': 'Markdown'},
                'discord': {'embed': True, 'thumbnail': True}
            },
            variables=['title', 'price', 'rating', 'category', 'shipping_time', 'source_platform', 'url'],
            description="Plantilla para productos de alta calidad"
        )
        
        # Plantilla para ofertas especiales
        templates['special_deal'] = NotificationTemplate(
            name="special_deal",
            template_type=TemplateType.MARKDOWN,
            subject_template="🔥 ¡OFERTA ESPECIAL DETECTADA!",
            body_template="""
🔥 **¡OFERTA ESPECIAL!** 🔥

**{title}**

💥 **PRECIO INCREÍBLE:** ${price}
⭐ **Rating:** {rating}/5.0 {rating_emoji}
⚡ **Categoría:** {category}
📦 **Envío:** {shipping_time} días
🎯 **Fuente:** {source_platform}

🚨 **¡PRECIO MUY BAJO!** 🚨
Esta oferta podría terminar pronto

{description_short}

🛒 [¡COMPRAR AHORA!]({url})

⏰ _{timestamp}_
            """.strip(),
            priority_styles={
                'low': {'emoji': '🔥', 'color': 0xff6600},
                'normal': {'emoji': '🔥', 'color': 0xff4400},
                'high': {'emoji': '🔥', 'color': 0xff2200},
                'urgent': {'emoji': '🔥', 'color': 0xff0000}
            },
            platform_specific={
                'telegram': {'parse_mode': 'Markdown'},
                'discord': {'embed': True, 'urgent_style': True}
            },
            variables=['title', 'price', 'rating', 'category', 'shipping_time', 'source_platform', 'url'],
            description="Plantilla para ofertas especiales"
        )
        
        # Plantilla para electrónicos
        templates['electronics'] = NotificationTemplate(
            name="electronics",
            template_type=TemplateType.MARKDOWN,
            subject_template="⚡ Nuevo Producto Electrónico",
            body_template="""
⚡ **ELECTRÓNICOS** ⚡

**{title}**

💰 **Precio:** ${price}
⭐ **Rating:** {rating}/5.0 {rating_emoji}
📱 **Categoría:** {category}
📦 **Envío:** {shipping_time} días
🔌 **Fuente:** {source_platform}

**Características:**
• Producto electrónico de calidad
• Precio competitivo
• Buenas valoraciones

{description_short}

🛒 [Ver Especificaciones]({url})

_{timestamp}_
            """.strip(),
            priority_styles={
                'low': {'emoji': '⚡', 'color': 0x4488ff},
                'normal': {'emoji': '⚡', 'color': 0x0066ff'},
                'high': {'emoji': '⚡', 'color': 0x0044ff'},
                'urgent': {'emoji': '⚡', 'color': 0x0022ff}
            },
            platform_specific={
                'telegram': {'parse_mode': 'Markdown'},
                'discord': {'embed': True, 'tech_style': True}
            },
            variables=['title', 'price', 'rating', 'category', 'shipping_time', 'source_platform', 'url'],
            description="Plantilla para productos electrónicos"
        )
        
        # Plantilla para productos premium
        templates['premium'] = NotificationTemplate(
            name="premium",
            template_type=TemplateType.MARKDOWN,
            subject_template="👑 Producto Premium Disponible",
            body_template="""
👑 **PRODUCTO PREMIUM** 👑

**{title}**

💎 **Inversión:** ${price}
⭐ **Excelencia:** {rating}/5.0 {rating_emoji}
🏆 **Categoría:** {category}
📦 **Envío:** {shipping_time} días
✨ **Plataforma:** {source_platform}

**Características Premium:**
• Producto de alto valor
• Rating excepcional
• Calidad superior

{description_short}

🛒 [Explorar Producto]({url})

_{timestamp}_
            """.strip(),
            priority_styles={
                'low': {'emoji': '👑', 'color': 0xffd700},
                'normal': {'emoji': '👑', 'color': 0xffcc00},
                'high': {'emoji': '👑', 'color': 0xffaa00},
                'urgent': {'emoji': '👑', 'color': 0xff8800}
            },
            platform_specific={
                'telegram': {'parse_mode': 'Markdown'},
                'discord': {'embed': True, 'premium_style': True}
            },
            variables=['title', 'price', 'rating', 'category', 'shipping_time', 'source_platform', 'url'],
            description="Plantilla para productos premium"
        )
        
        # Plantilla compacta
        templates['compact'] = NotificationTemplate(
            name="compact",
            template_type=TemplateType.TEXT,
            subject_template="Nuevo: {title}",
            body_template="""
{title}
💰 ${price} | ⭐ {rating}/5 | 📦 {shipping_time}d
🔗 {url}
            """.strip(),
            priority_styles={
                'low': {'emoji': '📝'},
                'normal': {'emoji': '📋'},
                'high': {'emoji': '⚠️'},
                'urgent': {'emoji': '🚨'}
            },
            platform_specific={
                'telegram': {'disable_preview': True},
                'discord': {'embed': False}
            },
            variables=['title', 'price', 'rating', 'shipping_time', 'url'],
            description="Plantilla compacta para notificaciones rápidas"
        )
        
        return templates
    
    def render_notification(self, 
                          template_name: str, 
                          product: Product, 
                          priority: NotificationPriority = NotificationPriority.NORMAL,
                          platform: str = "telegram") -> Dict[str, Any]:
        """
        Renderizar notificación usando una plantilla
        
        Args:
            template_name: Nombre de la plantilla
            product: Producto para la notificación
            priority: Prioridad de la notificación
            platform: Plataforma destino (telegram/discord)
            
        Returns:
            Dict con la notificación renderizada
        """
        if template_name not in self.templates:
            logger.warning(f"Plantilla {template_name} no encontrada, usando 'default'")
            template_name = 'default'
        
        template = self.templates[template_name]
        
        if not template.enabled:
            logger.warning(f"Plantilla {template_name} deshabilitada, usando 'default'")
            template = self.templates['default']
        
        # Preparar variables
        variables = self._prepare_variables(product, priority)
        
        # Renderizar plantilla
        try:
            subject = template.subject_template.format(**variables)
            body = template.body_template.format(**variables)
            
            # Aplicar estilos de prioridad
            priority_style = template.priority_styles.get(priority.value, {})
            
            # Adaptar para plataforma específica
            platform_config = template.platform_specific.get(platform, {})
            
            # Verificar límites de longitud
            body = self._check_length_limits(body, platform)
            
            notification = {
                'subject': subject,
                'body': body,
                'template_type': template.template_type.value,
                'priority': priority.value,
                'priority_style': priority_style,
                'platform_config': platform_config,
                'variables_used': list(variables.keys())
            }
            
            # Configuración específica para Discord embeds
            if platform == 'discord' and platform_config.get('embed', False):
                notification.update(self._create_discord_embed(
                    subject, body, product, priority_style, platform_config
                ))
            
            return notification
            
        except KeyError as e:
            logger.error(f"Variable {e} no encontrada en plantilla {template_name}")
            # Fallback a plantilla simple
            return self._create_fallback_notification(product, priority, platform)
        
        except Exception as e:
            logger.error(f"Error renderizando plantilla {template_name}: {e}")
            return self._create_fallback_notification(product, priority, platform)
    
    def _prepare_variables(self, product: Product, priority: NotificationPriority) -> Dict[str, Any]:
        """Preparar variables para la plantilla"""
        
        # Emojis de rating
        rating_emojis = {
            (0, 2): "😞",
            (2, 3): "😐", 
            (3, 4): "🙂",
            (4, 4.5): "😊",
            (4.5, 5): "🤩"
        }
        
        rating_float = float(product.rating) if product.rating else 0.0
        rating_emoji = "⭐"
        for (min_r, max_r), emoji in rating_emojis.items():
            if min_r <= rating_float < max_r:
                rating_emoji = emoji
                break
        
        # Descripción corta
        description = product.description or "Descripción no disponible"
        description_short = description[:150] + "..." if len(description) > 150 else description
        
        # Timestamp formateado
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        
        return {
            'title': product.title or "Producto sin título",
            'price': f"{float(product.price):.2f}" if product.price else "N/A",
            'rating': f"{rating_float:.1f}" if rating_float > 0 else "N/A",
            'rating_emoji': rating_emoji,
            'category': product.category or "Sin categoría",
            'shipping_time': product.shipping_time or "N/A",
            'source_platform': product.source_platform or "Desconocida",
            'url': product.url or "#",
            'description': description,
            'description_short': description_short,
            'timestamp': timestamp,
            'priority': priority.value,
            'priority_emoji': "🔴" if priority == NotificationPriority.URGENT else "🟡" if priority == NotificationPriority.HIGH else "🔵"
        }
    
    def _check_length_limits(self, text: str, platform: str) -> str:
        """Verificar y truncar texto según límites de plataforma"""
        limits = self.platform_limits.get(platform, {})
        max_length = limits.get('max_length', 4000)
        
        if len(text) > max_length:
            logger.warning(f"Texto truncado para {platform}: {len(text)} -> {max_length} caracteres")
            return text[:max_length-3] + "..."
        
        return text
    
    def _create_discord_embed(self, 
                            subject: str, 
                            body: str, 
                            product: Product, 
                            priority_style: Dict[str, Any],
                            platform_config: Dict[str, Any]) -> Dict[str, Any]:
        """Crear embed para Discord"""
        embed = {
            'embeds': [{
                'title': subject,
                'description': body,
                'color': priority_style.get('color', 0x0099ff),
                'timestamp': datetime.now().isoformat(),
                'footer': {
                    'text': f"Dropshipping Assistant | {product.source_platform}"
                }
            }]
        }
        
        # Agregar thumbnail si está disponible
        if platform_config.get('thumbnail') and product.image_url:
            embed['embeds'][0]['thumbnail'] = {'url': product.image_url}
        
        # Agregar fields para información estructurada
        fields = []
        
        if product.price:
            fields.append({
                'name': '💰 Precio',
                'value': f"${float(product.price):.2f}",
                'inline': True
            })
        
        if product.rating:
            fields.append({
                'name': '⭐ Rating',
                'value': f"{float(product.rating):.1f}/5.0",
                'inline': True
            })
        
        if product.shipping_time:
            fields.append({
                'name': '📦 Envío',
                'value': f"{product.shipping_time} días",
                'inline': True
            })
        
        if fields:
            embed['embeds'][0]['fields'] = fields
        
        return embed
    
    def _create_fallback_notification(self, 
                                    product: Product, 
                                    priority: NotificationPriority,
                                    platform: str) -> Dict[str, Any]:
        """Crear notificación de respaldo en caso de error"""
        simple_message = f"""
🆕 Nuevo Producto

{product.title}
💰 ${float(product.price):.2f} | ⭐ {float(product.rating):.1f}/5
🔗 {product.url}
        """.strip()
        
        return {
            'subject': 'Nuevo Producto',
            'body': simple_message,
            'template_type': 'text',
            'priority': priority.value,
            'priority_style': {'emoji': '📝'},
            'platform_config': {},
            'variables_used': ['fallback']
        }
    
    def add_template(self, template: NotificationTemplate):
        """Agregar nueva plantilla"""
        self.templates[template.name] = template
        logger.info(f"Plantilla agregada: {template.name}")
    
    def remove_template(self, template_name: str):
        """Eliminar plantilla"""
        if template_name in self.templates and template_name != 'default':
            del self.templates[template_name]
            logger.info(f"Plantilla eliminada: {template_name}")
        else:
            logger.warning(f"No se puede eliminar plantilla: {template_name}")
    
    def enable_template(self, template_name: str, enabled: bool = True):
        """Habilitar/deshabilitar plantilla"""
        if template_name in self.templates:
            self.templates[template_name].enabled = enabled
            logger.info(f"Plantilla {template_name} {'habilitada' if enabled else 'deshabilitada'}")
    
    def get_templates_summary(self) -> Dict[str, Any]:
        """Obtener resumen de todas las plantillas"""
        return {
            "total_templates": len(self.templates),
            "enabled_templates": len([t for t in self.templates.values() if t.enabled]),
            "templates": [
                {
                    "name": template.name,
                    "enabled": template.enabled,
                    "type": template.template_type.value,
                    "variables": template.variables,
                    "description": template.description
                }
                for template in self.templates.values()
            ]
        }
    
    def preview_template(self, template_name: str, sample_data: Dict[str, Any] = None) -> str:
        """Previsualizar plantilla con datos de muestra"""
        if template_name not in self.templates:
            return "Plantilla no encontrada"
        
        template = self.templates[template_name]
        
        # Datos de muestra por defecto
        if not sample_data:
            sample_data = {
                'title': 'Producto de Ejemplo',
                'price': '29.99',
                'rating': '4.5',
                'rating_emoji': '🤩',
                'category': 'Electronics',
                'shipping_time': '7-15',
                'source_platform': 'AliExpress',
                'url': 'https://example.com',
                'description_short': 'Este es un producto de ejemplo para previsualizar la plantilla.',
                'timestamp': datetime.now().strftime("%d/%m/%Y %H:%M")
            }
        
        try:
            subject = template.subject_template.format(**sample_data)
            body = template.body_template.format(**sample_data)
            return f"**{subject}**\n\n{body}"
        except Exception as e:
            return f"Error en previsualización: {e}"


# Instancia global del motor de plantillas
template_engine = NotificationTemplateEngine()