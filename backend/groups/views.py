from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from permissions.checker import get_permission_checker
from .models import Group
from .serializers import GroupSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """ViewSet for Group model."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        checker = get_permission_checker(user)
        
        if user.is_superuser:
            return Group.objects.all()
        
        # Filter based on permissions
        queryset = Group.objects.all()
        return checker.filter_queryset(queryset, 'groups', 'read')
    
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
        instance.clients.clear()
        instance.users.clear()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
