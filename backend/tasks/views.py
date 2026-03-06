from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Task, TaskType
from .serializers import TaskSerializer, TaskTypeSerializer
from permissions.checker import get_permission_checker


class TaskTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for TaskType model."""
    queryset = TaskType.objects.all()
    serializer_class = TaskTypeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return task types - readable by anyone with tasks read permission."""
        user = self.request.user
        checker = get_permission_checker(user)
        if not checker.has_permission('tasks', 'read'):
            return TaskType.objects.none()
        return TaskType.objects.all()

    def create(self, request, *args, **kwargs):
        """Create a new task type - requires manage permission."""
        if not self._has_permission(request.user, 'manage'):
            return Response(
                {'error': 'You do not have permission to create task types'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task_type = serializer.save()
        task_type.last_edit = timezone.now()
        task_type.last_edited_by = request.user
        task_type.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        """Update a task type - requires manage permission."""
        if not self._has_permission(request.user, 'manage'):
            return Response(
                {'error': 'You do not have permission to edit task types'},
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
        """Delete a task type - requires admin permission."""
        if not self._has_permission(request.user, 'admin'):
            return Response(
                {'error': 'You do not have permission to delete task types'},
                status=status.HTTP_403_FORBIDDEN
            )
        instance = self.get_object()
        task_count = instance.tasks.count()
        if task_count:
            return Response(
                {'error': f'Cannot delete task type. It has {task_count} linked task(s). Remove them first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def _has_permission(self, user, required_level):
        checker = get_permission_checker(user)
        return checker.has_permission('tasks', required_level)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for Task model."""
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter tasks based on user permissions."""
        user = self.request.user
        checker = get_permission_checker(user)

        queryset = Task.objects.select_related(
            'client', 'task_type', 'assigned_to', 'created_by'
        )

        # Filter by status query param (supports comma-separated values)
        task_status = self.request.query_params.get('status')
        if task_status:
            statuses = task_status.split(',')
            if len(statuses) > 1:
                queryset = queryset.filter(status__in=statuses)
            else:
                queryset = queryset.filter(status=task_status)

        # Filter by assigned_to query param
        assigned_to = self.request.query_params.get('assigned_to')
        if assigned_to:
            queryset = queryset.filter(assigned_to_id=assigned_to)

        # Filter by client query param
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(client_id=client_id)

        # Filter by task_type query param
        task_type_id = self.request.query_params.get('task_type')
        if task_type_id:
            queryset = queryset.filter(task_type_id=task_type_id)

        # Filter by client's group query param
        group_id = self.request.query_params.get('group')
        if group_id:
            queryset = queryset.filter(client__groups__id=group_id).distinct()

        return checker.filter_queryset(queryset, 'tasks', 'read')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a task and update last_access."""
        instance = self.get_object()
        instance.update_last_access()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new task."""
        if not self._has_permission(request.user, 'create'):
            return Response(
                {'error': 'You do not have permission to create tasks'},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(created_by=request.user)
        task.last_edit = timezone.now()
        task.last_edited_by = request.user
        task.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            TaskSerializer(task).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def update(self, request, *args, **kwargs):
        """Update a task."""
        instance = self.get_object()
        if not self._has_permission(request.user, 'edit', instance):
            return Response(
                {'error': 'You do not have permission to edit this task'},
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
        """Delete a task - requires manage permission."""
        instance = self.get_object()
        if not self._has_permission(request.user, 'manage', instance):
            return Response(
                {'error': 'You do not have permission to delete this task'},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='batch')
    def batch(self, request):
        """Batch operations on multiple tasks."""
        if not self._has_permission(request.user, 'edit'):
            return Response(
                {'error': 'You do not have permission to edit tasks'},
                status=status.HTTP_403_FORBIDDEN
            )

        task_ids = request.data.get('task_ids', [])
        batch_action = request.data.get('action')
        value = request.data.get('value')

        if not task_ids or not batch_action:
            return Response(
                {'error': 'task_ids and action are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tasks = Task.objects.filter(id__in=task_ids)
        count = tasks.count()

        if batch_action == 'complete':
            tasks.filter(status='active').update(status='completed')

        elif batch_action == 'cancel':
            tasks.filter(status='active').update(status='cancelled')

        elif batch_action == 'set_type':
            try:
                task_type = TaskType.objects.get(id=value)
            except TaskType.DoesNotExist:
                return Response({'error': 'Task type not found'}, status=status.HTTP_400_BAD_REQUEST)
            tasks.update(task_type=task_type)

        else:
            return Response({'error': f'Unknown action: {batch_action}'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'count': count, 'action': batch_action})

    def _has_permission(self, user, required_level, obj=None):
        checker = get_permission_checker(user)
        return checker.has_permission('tasks', required_level, obj)
