from rest_framework import serializers
from .models import Client
from users.models import Group, User
from users.serializers import GroupSerializer, UserSerializer


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for Client model."""
    groups = serializers.PrimaryKeyRelatedField(many=True, queryset=Group.objects.all(), required=False)
    assigned_users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    groups_detail = GroupSerializer(source='groups', many=True, read_only=True)
    assigned_users_detail = UserSerializer(source='assigned_users', many=True, read_only=True)
    
    class Meta:
        model = Client
        fields = [
            'id', 'first_name', 'last_name', 'phone', 'email', 'address',
            'groups', 'groups_detail', 'assigned_users', 'assigned_users_detail',
            'created_at', 'last_access', 'last_edit', 'last_edited_by'
        ]
        read_only_fields = ['id', 'created_at', 'last_access', 'last_edit', 'last_edited_by']
