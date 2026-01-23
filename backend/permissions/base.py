"""
Base permission system for CRM modules.
Each module should define its permission types and levels in a permissions.py file.
"""

from typing import List, Dict, Optional
from django.apps import apps


class PermissionDefinition:
    """Defines available permission types and levels for a module."""
    
    def __init__(self, module_name: str, types: List[str], levels: List[str]):
        """
        Initialize permission definition.
        
        Args:
            module_name: Name of the module (e.g., 'clients', 'users')
            types: List of ownership types (e.g., ['self', 'group', 'all'])
            levels: List of permission levels (e.g., ['read', 'create', 'edit', 'manage', 'admin'])
        """
        self.module_name = module_name
        self.types = types
        self.levels = levels
    
    def validate(self, perm_type: str, level: str) -> bool:
        """Validate if a permission type and level combination is valid."""
        return perm_type in self.types and level in self.levels


class PermissionRegistry:
    """Registry for all module permissions."""
    
    _instance = None
    _permissions: Dict[str, PermissionDefinition] = {}
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, module_name: str, types: List[str], levels: List[str]):
        """Register permissions for a module."""
        self._permissions[module_name] = PermissionDefinition(module_name, types, levels)
    
    def get(self, module_name: str) -> Optional[PermissionDefinition]:
        """Get permission definition for a module."""
        return self._permissions.get(module_name)
    
    def get_all(self) -> Dict[str, PermissionDefinition]:
        """Get all registered permissions."""
        return self._permissions.copy()
    
    def initialize(self):
        """Load permissions from all installed apps."""
        if self._initialized:
            return
        
        # Load permissions from all apps
        for app_config in apps.get_app_configs():
            try:
                # Try to import permissions module
                permissions_module = __import__(f'{app_config.name}.permissions', fromlist=[''])
                if hasattr(permissions_module, 'PERMISSION_TYPES') and hasattr(permissions_module, 'PERMISSION_LEVELS'):
                    module_name = getattr(permissions_module, 'MODULE_NAME', app_config.name)
                    types = permissions_module.PERMISSION_TYPES
                    levels = permissions_module.PERMISSION_LEVELS
                    self.register(module_name, types, levels)
            except (ImportError, AttributeError):
                # Module doesn't have permissions definition, skip
                pass
        
        self._initialized = True


# Global registry instance
registry = PermissionRegistry()


def get_permission_registry() -> PermissionRegistry:
    """Get the global permission registry."""
    registry.initialize()
    return registry
