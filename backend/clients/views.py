from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Client
from .serializers import ClientSerializer
from users.models import User, Group, Role


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet for Client model."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter clients based on user permissions."""
        user = self.request.user
        
        # Superusers can see all clients
        if user.is_superuser:
            return Client.objects.all()
        
        # Get user's roles and check permissions
        user_roles = user.roles.all()
        queryset = Client.objects.none()
        
        for role in user_roles:
            perm = role.get_module_permission('clients')
            if not perm:
                continue
            
            ownership = perm.get('ownership', 'self')
            level = perm.get('level', 'read')
            
            if ownership == 'self':
                # Only clients assigned to this user
                queryset = queryset | Client.objects.filter(assigned_users=user)
            elif ownership == 'group':
                # Clients assigned to user's groups
                user_groups = user.crm_groups.all()
                queryset = queryset | Client.objects.filter(groups__in=user_groups)
                # Also include directly assigned clients
                queryset = queryset | Client.objects.filter(assigned_users=user)
        
        return queryset.distinct()
    
    def get_serializer_context(self):
        """Add request to serializer context."""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a client and update last_access."""
        instance = self.get_object()
        instance.update_last_access()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Create a new client."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Check create permission
        if not self._has_permission(request.user, 'create'):
            return Response(
                {'error': 'You do not have permission to create clients'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        client = serializer.save()
        client.last_edit = timezone.now()
        client.last_edited_by = request.user
        client.save()
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def update(self, request, *args, **kwargs):
        """Update a client."""
        instance = self.get_object()
        
        # Check edit permission
        if not self._has_permission(request.user, 'edit', instance):
            return Response(
                {'error': 'You do not have permission to edit this client'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        instance.last_edit = timezone.now()
        instance.last_edited_by = request.user
        instance.save()
        
        self.perform_update(serializer)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Delete a client."""
        instance = self.get_object()
        
        # Check manage permission for deletion
        if not self._has_permission(request.user, 'manage', instance):
            return Response(
                {'error': 'You do not have permission to delete this client'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def _has_permission(self, user, required_level, obj=None):
        """Check if user has required permission level."""
        if user.is_superuser:
            return True
        
        user_roles = user.roles.all()
        for role in user_roles:
            perm = role.get_module_permission('clients')
            if not perm:
                continue
            
            ownership = perm.get('ownership', 'self')
            level = perm.get('level', 'read')
            
            # Determine ownership type for this object
            ownership_type = 'self'
            if obj:
                if obj.assigned_users.filter(id=user.id).exists():
                    ownership_type = 'self'
                elif obj.groups.filter(id__in=user.crm_groups.values_list('id', flat=True)).exists():
                    ownership_type = 'group'
                else:
                    ownership_type = 'self'  # Default
            
            if role.has_permission('clients', required_level, ownership_type, user, obj):
                return True
        
        return False
