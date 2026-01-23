from django.db import models
from users.models import User


class Role(models.Model):
    """Role model with permissions for modules."""
    
    name = models.CharField(max_length=150, unique=True)
    is_active = models.BooleanField(default=True)
    users = models.ManyToManyField(User, related_name='roles', blank=True)
    
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


class RolePermission(models.Model):
    """Individual permission row for a role."""
    
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='permissions')
    module_name = models.CharField(max_length=100)
    ownership_type = models.CharField(max_length=20)  # 'self', 'group', 'all'
    level = models.CharField(max_length=20)  # 'read', 'create', 'edit', 'manage', 'admin'
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'role_permissions'
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = [['role', 'module_name', 'ownership_type', 'level']]
        ordering = ['module_name', 'ownership_type', 'level']
    
    def __str__(self):
        return f"{self.role.name} - {self.module_name}: {self.ownership_type} {self.level}"
