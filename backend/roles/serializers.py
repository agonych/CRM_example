from rest_framework import serializers
from .models import Role, RolePermission
from users.models import User


class RolePermissionSerializer(serializers.ModelSerializer):
    """Serializer for RolePermission model."""
    
    class Meta:
        model = RolePermission
        fields = ['id', 'module_name', 'ownership_type', 'level', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    user_count = serializers.SerializerMethodField()
    permissions = RolePermissionSerializer(many=True, read_only=True, source='permissions.all')
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'is_active', 'users', 'user_count', 'permissions',
            'created_at', 'last_access', 'last_edit', 'last_edited_by'
        ]
        read_only_fields = ['id', 'created_at', 'last_access', 'last_edit', 'last_edited_by']
    
    def get_user_count(self, obj):
        return obj.users.count()
