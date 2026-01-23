from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .base import get_permission_registry


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_available_permissions(request):
    """Get all available module permissions for role configuration."""
    registry = get_permission_registry()
    permissions = registry.get_all()
    
    result = {}
    for module_name, perm_def in permissions.items():
        result[module_name] = {
            'types': perm_def.types,
            'levels': perm_def.levels,
        }
    
    return Response(result)
