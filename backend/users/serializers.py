from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User
from groups.models import Group
from roles.models import Role


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    groups = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Group.objects.all(), required=False, source='crm_groups'
    )
    roles = serializers.SerializerMethodField()
    group_names = serializers.SerializerMethodField()
    role_names = serializers.SerializerMethodField()
    assigned_clients_count = serializers.SerializerMethodField()
    assigned_tasks_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'first_name', 'last_name', 'email', 'password',
            'is_active', 'is_superuser',
            'created_at', 'last_access', 'last_edit', 'last_edited_by',
            'groups', 'group_names', 'roles', 'role_names',
            'assigned_clients_count', 'assigned_tasks_count',
        ]
        read_only_fields = ['id', 'created_at', 'last_access', 'last_edit', 'last_edited_by']
    
    def create(self, validated_data):
        groups = validated_data.pop('crm_groups', [])
        password = validated_data.pop('password', None)
        user = User.objects.create_user(password=password, **validated_data)
        if groups:
            user.crm_groups.set(groups)
        return user
    
    def get_group_names(self, obj):
        return [g.name for g in obj.crm_groups.all()]

    def get_roles(self, obj):
        """Get role IDs for the user."""
        return [role.id for role in obj.roles.all()]

    def get_role_names(self, obj):
        return [r.name for r in obj.roles.all()]

    def get_assigned_clients_count(self, obj):
        return obj.assigned_clients.count()

    def get_assigned_tasks_count(self, obj):
        return obj.assigned_tasks.count()
    
    def update(self, instance, validated_data):
        groups = validated_data.pop('crm_groups', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        if groups is not None:
            instance.crm_groups.set(groups)
        
        instance.save()
        return instance


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


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    users = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all(), required=False)
    user_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = [
            'id', 'name', 'is_active', 'users', 'user_count', 'permissions',
            'created_at', 'last_access', 'last_edit', 'last_edited_by'
        ]
        read_only_fields = ['id', 'created_at', 'last_access', 'last_edit', 'last_edited_by']
    
    def get_user_count(self, obj):
        return obj.users.count()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)
