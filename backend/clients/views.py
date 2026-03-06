from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Client, ClientStatus
from .serializers import ClientSerializer, ClientStatusSerializer
from groups.models import Group
from users.models import User
from permissions.checker import get_permission_checker


class ClientStatusViewSet(viewsets.ModelViewSet):
    """ViewSet for ClientStatus model."""
    queryset = ClientStatus.objects.all()
    serializer_class = ClientStatusSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        checker = get_permission_checker(user)
        if not checker.has_permission('clients', 'read'):
            return ClientStatus.objects.none()
        return ClientStatus.objects.all()

    def create(self, request, *args, **kwargs):
        if not self._has_permission(request.user, 'manage'):
            return Response(
                {'error': 'You do not have permission to create client statuses'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        obj.last_edit = timezone.now()
        obj.last_edited_by = request.user
        obj.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        if not self._has_permission(request.user, 'manage'):
            return Response(
                {'error': 'You do not have permission to edit client statuses'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance.last_edit = timezone.now()
        instance.last_edited_by = request.user
        instance.save()
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        if not self._has_permission(request.user, 'admin'):
            return Response(
                {'error': 'You do not have permission to delete client statuses'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        instance.clients.update(status=None)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _has_permission(self, user, required_level):
        checker = get_permission_checker(user)
        return checker.has_permission('clients', required_level)


class ClientViewSet(viewsets.ModelViewSet):
    """ViewSet for Client model."""
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter clients based on user permissions."""
        user = self.request.user
        checker = get_permission_checker(user)

        queryset = Client.objects.select_related('status')

        # Filter by status query param
        status_id = self.request.query_params.get('status')
        if status_id:
            if status_id == 'null':
                queryset = queryset.filter(status__isnull=True)
            else:
                queryset = queryset.filter(status_id=status_id)

        # Filter by group query param
        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(groups__id=group_id)

        # Filter by assigned user
        assigned_user = self.request.query_params.get('assigned_user')
        if assigned_user:
            queryset = queryset.filter(assigned_users__id=assigned_user)

        return checker.filter_queryset(queryset, 'clients', 'read')

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

        task_count = instance.tasks.count()
        if task_count:
            return Response(
                {'error': f'Cannot delete client. They have {task_count} linked task(s). Remove them first.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='batch')
    def batch(self, request):
        """Batch operations on multiple clients."""
        if not self._has_permission(request.user, 'edit'):
            return Response(
                {'error': 'You do not have permission to edit clients'},
                status=status.HTTP_403_FORBIDDEN
            )

        client_ids = request.data.get('client_ids', [])
        batch_action = request.data.get('action')
        value = request.data.get('value')

        if not client_ids or not batch_action:
            return Response(
                {'error': 'client_ids and action are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        clients = Client.objects.filter(id__in=client_ids)
        count = clients.count()

        if batch_action == 'change_status':
            status_id = value if value else None
            if status_id:
                try:
                    ClientStatus.objects.get(id=status_id)
                except ClientStatus.DoesNotExist:
                    return Response({'error': 'Status not found'}, status=status.HTTP_400_BAD_REQUEST)
            clients.update(status_id=status_id)

        elif batch_action == 'add_to_group':
            try:
                group = Group.objects.get(id=value)
            except Group.DoesNotExist:
                return Response({'error': 'Group not found'}, status=status.HTTP_400_BAD_REQUEST)
            for client in clients:
                client.groups.add(group)

        elif batch_action == 'remove_from_group':
            try:
                group = Group.objects.get(id=value)
            except Group.DoesNotExist:
                return Response({'error': 'Group not found'}, status=status.HTTP_400_BAD_REQUEST)
            for client in clients:
                client.groups.remove(group)

        elif batch_action == 'assign_users':
            user_ids = value if isinstance(value, list) else [value]
            users = User.objects.filter(id__in=user_ids)
            for client in clients:
                client.assigned_users.set(users)

        else:
            return Response({'error': f'Unknown action: {batch_action}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'count': count, 'action': batch_action})

    def _has_permission(self, user, required_level, obj=None):
        """Check if user has required permission level."""
        checker = get_permission_checker(user)
        return checker.has_permission('clients', required_level, obj)
