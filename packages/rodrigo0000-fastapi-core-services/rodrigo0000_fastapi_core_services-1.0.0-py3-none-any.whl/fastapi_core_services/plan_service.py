"""
Plan service - Generic plan management for SaaS
Basado en el patrón de Autogrid
"""

from enum import Enum
from typing import Dict, Any, Optional, List
import os

class PlanType(Enum):
    """Plan types enum"""
    FREE = "free"
    PRO = "pro"
    UNLIMITED = "unlimited"

class PlanFeature(Enum):
    """Plan features enum"""
    MAX_ITEMS = "max_items"
    MAX_OPERATIONS = "max_operations"
    EXPORT_DATA = "export_data"
    PRIORITY_SUPPORT = "priority_support"
    API_ACCESS = "api_access"
    CUSTOM_INTEGRATIONS = "custom_integrations"

class PlanService:
    """Generic plan management service"""
    
    # Default plan configuration - can be overridden
    DEFAULT_PLANS = {
        PlanType.FREE.value: {
            'name': 'Free',
            'stripe_price_id': os.getenv('STRIPE_FREE_PLAN_PRICE_ID'),
            'max_items': 10,
            'max_operations': 50,
            'export_data': False,
            'priority_support': False,
            'api_access': False,
            'custom_integrations': False,
            'description': 'Plan gratuito con funcionalidades básicas',
            'features': [
                'Hasta 50 operaciones por mes',
                'Almacenamiento para 10 elementos',
                'Soporte básico por correo electrónico'
            ]
        },
        PlanType.PRO.value: {
            'name': 'Pro',
            'stripe_price_id': os.getenv('STRIPE_PRO_PLAN_PRICE_ID'),
            'max_items': 100,
            'max_operations': 1000,
            'export_data': True,
            'priority_support': False,
            'api_access': True,
            'custom_integrations': False,
            'description': 'Plan profesional para usuarios avanzados',
            'features': [
                'Hasta 1,000 operaciones por mes',
                'Almacenamiento para 100 elementos',
                'Exportación de datos',
                'Acceso a API',
                'Soporte por email'
            ]
        },
        PlanType.UNLIMITED.value: {
            'name': 'Unlimited',
            'stripe_price_id': os.getenv('STRIPE_UNLIMITED_PLAN_PRICE_ID'),
            'max_items': -1,  # -1 means unlimited
            'max_operations': -1,  # -1 means unlimited
            'export_data': True,
            'priority_support': True,
            'api_access': True,
            'custom_integrations': True,
            'description': 'Plan ilimitado para uso empresarial',
            'features': [
                'Operaciones ilimitadas',
                'Almacenamiento ilimitado',
                'Exportación de datos',
                'Acceso completo a API',
                'Integraciones personalizadas',
                'Soporte prioritario'
            ]
        }
    }
    
    def __init__(self, custom_plans: Optional[Dict] = None):
        """
        Initialize plan service
        
        Args:
            custom_plans: Custom plan configuration to override defaults
        """
        self.plans = custom_plans or self.DEFAULT_PLANS
    
    def get_plan(self, plan_type: str) -> Optional[Dict[str, Any]]:
        """Get plan configuration by type"""
        return self.plans.get(plan_type)
    
    def get_all_plans(self) -> Dict[str, Dict[str, Any]]:
        """Get all available plans"""
        return self.plans
    
    def get_plan_limits(self, plan_type: str) -> Dict[str, Any]:
        """Get plan limits for validation"""
        plan = self.get_plan(plan_type)
        if not plan:
            return {}
        
        return {
            'max_items': plan.get('max_items', 0),
            'max_operations': plan.get('max_operations', 0),
            'export_data': plan.get('export_data', False),
            'priority_support': plan.get('priority_support', False),
            'api_access': plan.get('api_access', False),
            'custom_integrations': plan.get('custom_integrations', False)
        }
    
    def can_perform_operation(self, plan_type: str, current_usage: int, operation_type: str = 'operations') -> bool:
        """
        Check if user can perform an operation based on their plan
        
        Args:
            plan_type: User's plan type
            current_usage: Current usage count
            operation_type: Type of operation ('operations' or 'items')
            
        Returns:
            bool: True if operation is allowed
        """
        plan = self.get_plan(plan_type)
        if not plan:
            return False
        
        limit_key = f'max_{operation_type}'
        limit = plan.get(limit_key, 0)
        
        # -1 means unlimited
        if limit == -1:
            return True
        
        return current_usage < limit
    
    def has_feature(self, plan_type: str, feature: str) -> bool:
        """Check if plan has a specific feature"""
        plan = self.get_plan(plan_type)
        if not plan:
            return False
        
        return plan.get(feature, False)
    
    def get_upgrade_suggestions(self, plan_type: str) -> List[str]:
        """Get upgrade suggestions based on current plan"""
        if plan_type == PlanType.FREE.value:
            return [PlanType.PRO.value, PlanType.UNLIMITED.value]
        elif plan_type == PlanType.PRO.value:
            return [PlanType.UNLIMITED.value]
        else:
            return []
