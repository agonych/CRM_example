from django.contrib import admin
from .models import Group


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'last_edited_by')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    filter_horizontal = ('users',)
