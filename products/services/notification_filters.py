"""
🔔 Sistema Avanzado de Filtros de Notificaciones
Filtros inteligentes, plantillas personalizadas y alertas condicionales
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from django.conf import settings
from products.models import Product

logger = logging.getLogger('notifications')


class FilterOperator(Enum):
    """Operadores para filtros de notificaciones"""
    EQUALS = "eq"
    NOT_EQUALS = "ne"
    GREATER_THAN = "gt"
    GREATER_EQUAL = "gte"
    LESS_THAN = "lt"
    LESS_EQUAL = "lte"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN_LIST = "in"
    NOT_IN_LIST = "not_in"
    REGEX = "regex"


class NotificationPriority(Enum):
    """Prioridades de notificación"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class NotificationFilter:
    """Filtro individual para notificaciones"""
    field: str
    operator: FilterOperator
    value: Any
    enabled: bool = True
    name: str = ""
    description: str = ""
    
    def __post_init__(self):
        if not self.name:
            self.name = f"{self.field}_{self.operator.value}_{str(self.value)[:20]}"


@dataclass
class NotificationRule:
    """Regla de notificación con filtros y condiciones"""
    name: str
    filters: List[NotificationFilter] = field(default_factory=list)
    priority: NotificationPriority = NotificationPriority.NORMAL
    enabled: bool = True
    platforms: List[str] = field(default_factory=lambda: ["telegram", "discord"])
    template: str = "default"
    rate_limit_minutes: int = 0  # 0 = sin límite
    max_notifications_per_hour: int = 0  # 0 = sin límite
    schedule_start_hour: int = 0  # 0-23
    schedule_end_hour: int = 23  # 0-23
    weekdays_only: bool = False
    description: str = ""
    
    def __post_init__(self):
        if not self.description:
            self.description = f"Regla para {self.name}"


class NotificationFilterEngine:
    """Motor de filtros para notificaciones"""
    
    def __init__(self):
        self.rules = self._load_default_rules()
        self.notification_history = {}  # Para rate limiting
    
    def _load_default_rules(self) -> List[NotificationRule]:
        """Cargar reglas por defecto"""
        return [
            # Regla para productos de alta calidad
            NotificationRule(
                name="high_quality_products",
                filters=[
                    NotificationFilter("rating", FilterOperator.GREATER_EQUAL, 4.5),
                    NotificationFilter("price", FilterOperator.LESS_EQUAL, 100.0),
                    NotificationFilter("source_platform", FilterOperator.EQUALS, "aliexpress")
                ],
                priority=NotificationPriority.HIGH,
                template="high_quality",
                description="Productos con rating alto y precio razonable"
            ),
            
            # Regla para ofertas especiales
            NotificationRule(
                name="special_deals",
                filters=[
                    NotificationFilter("price", FilterOperator.LESS_THAN, 20.0),
                    NotificationFilter("rating", FilterOperator.GREATER_THAN, 4.0),
                    NotificationFilter("category", FilterOperator.IN_LIST, ["Electronics", "Home & Garden"])
                ],
                priority=NotificationPriority.URGENT,
                template="special_deal",
                max_notifications_per_hour=5,
                description="Ofertas especiales con precio muy bajo"
            ),
            
            # Regla para electrónicos populares
            NotificationRule(
                name="popular_electronics",
                filters=[
                    NotificationFilter("category", FilterOperator.EQUALS, "Electronics"),
                    NotificationFilter("title", FilterOperator.CONTAINS, "wireless"),
                    NotificationFilter("price", FilterOperator.LESS_THAN, 50.0)
                ],
                priority=NotificationPriority.NORMAL,
                template="electronics",
                rate_limit_minutes=30,
                description="Productos electrónicos populares"
            ),
            
            # Regla para productos premium
            NotificationRule(
                name="premium_products",
                filters=[
                    NotificationFilter("price", FilterOperator.GREATER_THAN, 100.0),
                    NotificationFilter("rating", FilterOperator.GREATER_EQUAL, 4.7)
                ],
                priority=NotificationPriority.LOW,
                template="premium",
                schedule_start_hour=9,
                schedule_end_hour=18,
                weekdays_only=True,
                description="Productos premium de alto valor"
            )
        ]
    
    def evaluate_product(self, product: Product) -> List[NotificationRule]:
        """
        Evaluar un producto contra todas las reglas activas
        
        Args:
            product: Producto a evaluar
            
        Returns:
            List[NotificationRule]: Reglas que coinciden con el producto
        """
        matching_rules = []
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # Verificar horario y días
            if not self._check_schedule(rule):
                continue
            
            # Verificar rate limiting
            if not self._check_rate_limit(rule):
                continue
            
            # Evaluar filtros
            if self._evaluate_filters(product, rule.filters):
                matching_rules.append(rule)
                logger.info(f"Producto {product.title} coincide con regla '{rule.name}'")
        
        return matching_rules
    
    def _evaluate_filters(self, product: Product, filters: List[NotificationFilter]) -> bool:
        """
        Evaluar todos los filtros de una regla
        
        Args:
            product: Producto a evaluar
            filters: Lista de filtros a aplicar
            
        Returns:
            bool: True si todos los filtros pasan (AND lógico)
        """
        for filter_obj in filters:
            if not filter_obj.enabled:
                continue
            
            if not self._evaluate_single_filter(product, filter_obj):
                return False
        
        return True
    
    def _evaluate_single_filter(self, product: Product, filter_obj: NotificationFilter) -> bool:
        """
        Evaluar un filtro individual
        
        Args:
            product: Producto a evaluar
            filter_obj: Filtro a aplicar
            
        Returns:
            bool: True si el filtro pasa
        """
        try:
            # Obtener valor del campo del producto
            field_value = self._get_field_value(product, filter_obj.field)
            
            if field_value is None:
                return False
            
            # Aplicar operador
            return self._apply_operator(field_value, filter_obj.operator, filter_obj.value)
            
        except Exception as e:
            logger.error(f"Error evaluando filtro {filter_obj.name}: {e}")
            return False
    
    def _get_field_value(self, product: Product, field: str) -> Any:
        """Obtener valor de un campo del producto"""
        field_mapping = {
            'title': product.title,
            'price': float(product.price) if product.price else 0.0,
            'rating': float(product.rating) if product.rating else 0.0,
            'category': product.category,
            'source_platform': product.source_platform,
            'shipping_time': product.shipping_time or 0,
            'url': product.url,
            'created_at': product.created_at
        }
        
        return field_mapping.get(field)
    
    def _apply_operator(self, field_value: Any, operator: FilterOperator, filter_value: Any) -> bool:
        """Aplicar operador de comparación"""
        if operator == FilterOperator.EQUALS:
            return field_value == filter_value
        
        elif operator == FilterOperator.NOT_EQUALS:
            return field_value != filter_value
        
        elif operator == FilterOperator.GREATER_THAN:
            return field_value > filter_value
        
        elif operator == FilterOperator.GREATER_EQUAL:
            return field_value >= filter_value
        
        elif operator == FilterOperator.LESS_THAN:
            return field_value < filter_value
        
        elif operator == FilterOperator.LESS_EQUAL:
            return field_value <= filter_value
        
        elif operator == FilterOperator.CONTAINS:
            return str(filter_value).lower() in str(field_value).lower()
        
        elif operator == FilterOperator.NOT_CONTAINS:
            return str(filter_value).lower() not in str(field_value).lower()
        
        elif operator == FilterOperator.STARTS_WITH:
            return str(field_value).lower().startswith(str(filter_value).lower())
        
        elif operator == FilterOperator.ENDS_WITH:
            return str(field_value).lower().endswith(str(filter_value).lower())
        
        elif operator == FilterOperator.IN_LIST:
            return field_value in filter_value
        
        elif operator == FilterOperator.NOT_IN_LIST:
            return field_value not in filter_value
        
        elif operator == FilterOperator.REGEX:
            return bool(re.search(str(filter_value), str(field_value), re.IGNORECASE))
        
        return False
    
    def _check_schedule(self, rule: NotificationRule) -> bool:
        """Verificar si la regla debe ejecutarse según el horario"""
        now = datetime.now()
        
        # Verificar día de la semana
        if rule.weekdays_only and now.weekday() >= 5:  # 5=Sábado, 6=Domingo
            return False
        
        # Verificar horario
        current_hour = now.hour
        if rule.schedule_start_hour <= rule.schedule_end_hour:
            # Horario normal (ej: 9-18)
            if not (rule.schedule_start_hour <= current_hour <= rule.schedule_end_hour):
                return False
        else:
            # Horario nocturno (ej: 22-6)
            if not (current_hour >= rule.schedule_start_hour or current_hour <= rule.schedule_end_hour):
                return False
        
        return True
    
    def _check_rate_limit(self, rule: NotificationRule) -> bool:
        """Verificar rate limiting para una regla"""
        now = datetime.now()
        rule_key = f"rule_{rule.name}"
        
        if rule_key not in self.notification_history:
            self.notification_history[rule_key] = []
        
        # Limpiar historial antiguo
        cutoff_time = now - timedelta(hours=1)
        self.notification_history[rule_key] = [
            timestamp for timestamp in self.notification_history[rule_key] 
            if timestamp > cutoff_time
        ]
        
        # Verificar rate limit por minutos
        if rule.rate_limit_minutes > 0:
            cutoff_minutes = now - timedelta(minutes=rule.rate_limit_minutes)
            recent_notifications = [
                timestamp for timestamp in self.notification_history[rule_key]
                if timestamp > cutoff_minutes
            ]
            if recent_notifications:
                logger.debug(f"Regla {rule.name} en rate limit por {rule.rate_limit_minutes} minutos")
                return False
        
        # Verificar máximo por hora
        if rule.max_notifications_per_hour > 0:
            if len(self.notification_history[rule_key]) >= rule.max_notifications_per_hour:
                logger.debug(f"Regla {rule.name} alcanzó máximo de {rule.max_notifications_per_hour} notificaciones por hora")
                return False
        
        # Registrar esta notificación
        self.notification_history[rule_key].append(now)
        return True
    
    def add_rule(self, rule: NotificationRule):
        """Agregar nueva regla"""
        self.rules.append(rule)
        logger.info(f"Regla agregada: {rule.name}")
    
    def remove_rule(self, rule_name: str):
        """Eliminar regla por nombre"""
        self.rules = [rule for rule in self.rules if rule.name != rule_name]
        logger.info(f"Regla eliminada: {rule_name}")
    
    def enable_rule(self, rule_name: str, enabled: bool = True):
        """Habilitar/deshabilitar regla"""
        for rule in self.rules:
            if rule.name == rule_name:
                rule.enabled = enabled
                logger.info(f"Regla {rule_name} {'habilitada' if enabled else 'deshabilitada'}")
                break
    
    def get_rules_summary(self) -> Dict[str, Any]:
        """Obtener resumen de todas las reglas"""
        return {
            "total_rules": len(self.rules),
            "enabled_rules": len([r for r in self.rules if r.enabled]),
            "rules": [
                {
                    "name": rule.name,
                    "enabled": rule.enabled,
                    "priority": rule.priority.value,
                    "filters_count": len(rule.filters),
                    "platforms": rule.platforms,
                    "description": rule.description
                }
                for rule in self.rules
            ]
        }


# Instancia global del motor de filtros
filter_engine = NotificationFilterEngine()