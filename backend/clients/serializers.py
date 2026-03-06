from rest_framework import serializers
from .models import Client, ClientStatus
from groups.models import Group
from users.models import User
from groups.serializers import GroupSerializer
from users.serializers import UserSerializer


class ClientStatusSerializer(serializers.ModelSerializer):
    """Serializer for ClientStatus model."""
    client_count = serializers.SerializerMethodField()

    class Meta:
        model = ClientStatus
        fields = ['id', 'name', 'sort_order', 'is_active', 'client_count', 'created_at', 'last_edit', 'last_edited_by']
        read_only_fields = ['id', 'created_at', 'last_edit', 'last_edited_by']

    def get_client_count(self, obj):
        return obj.clients.count()


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all(), required=False)
    assigned_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    groups_detail = GroupSerializer(source='groups', many=True, read_only=True)
    assigned_users_detail = UserSerializer(source='assigned_users', many=True, read_only=True)
    status_detail = ClientStatusSerializer(source='status', read_only=True)
    group_names = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'email', 'address',
            'status', 'status_detail',
            'groups', 'groups_detail', 'group_names',
            'assigned_users', 'assigned_users_detail',
            'created_at', 'last_access', 'last_edit', 'last_edited_by'
        ]
        read_only_fields = ['id', 'created_at', 'last_access', 'last_edit', 'last_edited_by']

    def get_group_names(self, obj):
        return [g.name for g in obj.groups.all()]
