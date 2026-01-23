from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'permissions'
    
    def ready(self):
        """Initialize permission registry when app is ready."""
        from .base import get_permission_registry
        get_permission_registry()
