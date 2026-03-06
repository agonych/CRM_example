from rest_framework import serializers
from .models import Group
from users.models import User


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for Group model."""
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    user_count = serializers.SerializerMethodField()
    client_count = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = [
            'id', 'name', 'is_active', 'users', 'user_count', 'client_count',
            'created_at', 'last_access', 'last_edit', 'last_edited_by'
        ]
        read_only_fields = ['id', 'created_at', 'last_access', 'last_edit', 'last_edited_by']

    def get_user_count(self, obj):
        return obj.users.count()

    def get_client_count(self, obj):
        return obj.clients.count()
