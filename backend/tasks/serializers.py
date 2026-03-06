from rest_framework import serializers
from .models import Task, TaskType
from users.serializers import UserSerializer
from clients.serializers import ClientSerializer


class TaskTypeSerializer(serializers.ModelSerializer):
    """Serializer for TaskType model."""
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = TaskType
        fields = ['id', 'name', 'is_active', 'task_count', 'created_at', 'last_edit', 'last_edited_by']
        read_only_fields = ['id', 'created_at', 'last_edit', 'last_edited_by']

    def get_task_count(self, obj):
        return obj.tasks.count()


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model."""
    client_detail = ClientSerializer(source='client', read_only=True)
    task_type_detail = TaskTypeSerializer(source='task_type', read_only=True)
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'description',
            'client', 'client_detail',
            'task_type', 'task_type_detail',
            'assigned_to', 'assigned_to_detail',
            'due_date', 'duration', 'monetary_value', 'status',
            'created_at', 'created_by', 'created_by_detail',
            'last_access', 'last_edit', 'last_edited_by',
        ]
        read_only_fields = ['id', 'created_at', 'created_by', 'last_access', 'last_edit', 'last_edited_by']
