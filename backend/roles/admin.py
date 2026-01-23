from django.contrib import admin
from .models import Role, RolePermission


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'last_edited_by')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('users',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module_name', 'ownership_type', 'level', 'is_active')
    list_filter = ('module_name', 'ownership_type', 'level', 'is_active')
    search_fields = ('role__name', 'module_name')
