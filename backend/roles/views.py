from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from permissions.checker import get_permission_checker
from .models import Role, RolePermission
from .serializers import RoleSerializer, RolePermissionSerializer


class RoleViewSet(viewsets.ModelViewSet):
    """ViewSet for Role model."""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        checker = get_permission_checker(user)
        
        if user.is_superuser:
            return Role.objects.all()
        
        # Filter based on permissions
        queryset = Role.objects.all()
        return checker.filter_queryset(queryset, 'roles', 'read')
    
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        instance.last_edit = timezone.now()
        instance.last_edited_by = request.user
        instance.save()
        
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user_count = instance.users.count()
        if user_count:
            return Response(
                {'error': f'Cannot delete role. It has {user_count} assigned user(s). Remove them first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RolePermissionViewSet(viewsets.ModelViewSet):
    """ViewSet for RolePermission model."""
    queryset = RolePermission.objects.all()
    serializer_class = RolePermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        role_id = self.request.query_params.get('role', None)
        if role_id:
            return RolePermission.objects.filter(role_id=role_id)
        return RolePermission.objects.all()
