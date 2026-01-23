from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):
    """Manager for custom user model."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser."""
        extra_fields.setdefault('is_user', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model."""
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_user = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_users'
    )
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    @property
    def is_staff(self):
        return self.is_superuser
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


class Group(models.Model):
    """Group model for organizing users."""
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='crm_groups', blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_groups'
    )
    
    class Meta:
        db_table = 'groups'
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
    
    def __str__(self):
        return self.name


class Role(models.Model):
    """Role model with permissions for modules."""
    
    # Permission levels
    LEVEL_CHOICES = [
        ('read', 'Read'),
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('manage', 'Manage'),
        ('admin', 'Admin'),
    ]
    
    # Ownership types
    OWNERSHIP_CHOICES = [
        ('self', 'Self'),
        ('group', 'Group'),
    ]
    
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='roles', blank=True)
    
    # Permissions stored as JSON
    # Format: {"module_name": {"ownership": "self|group", "level": "read|create|edit|manage|admin", "special": []}}
    permissions = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    last_access = models.DateTimeField(null=True, blank=True)
    last_edit = models.DateTimeField(null=True, blank=True)
    last_edited_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='edited_roles'
    )
    
    class Meta:
        db_table = 'roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name
    
    def set_module_permission(self, module_name, ownership, level, special_permissions=None):
        """Set permission for a specific module."""
        if not self.permissions:
            self.permissions = {}
        
        self.permissions[module_name] = {
            'ownership': ownership,
            'level': level,
            'special': special_permissions or []
        }
        self.save()
    
    def get_module_permission(self, module_name):
        """Get permission for a specific module."""
        return self.permissions.get(module_name, {})
    
    def has_permission(self, module_name, required_level, ownership_type='self', user=None, obj=None):
        """Check if role has required permission level for a module."""
        module_perm = self.get_module_permission(module_name)
        if not module_perm:
            return False
        
        level = module_perm.get('level', '')
        ownership = module_perm.get('ownership', 'self')
        
        # Check ownership match
        if ownership_type == 'self' and ownership != 'self':
            return False
        if ownership_type == 'group' and ownership not in ['self', 'group']:
            return False
        
        # Check level hierarchy
        level_hierarchy = ['read', 'create', 'edit', 'manage', 'admin']
        try:
            current_level_index = level_hierarchy.index(level)
            required_level_index = level_hierarchy.index(required_level)
            return current_level_index >= required_level_index
        except ValueError:
            return False
