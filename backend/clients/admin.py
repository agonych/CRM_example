from django.contrib import admin
from .models import Client


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'created_at', 'last_edited_by')
    list_filter = ('created_at', 'last_edit')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    filter_horizontal = ('groups', 'assigned_users')
