"""
URL configuration for crm_project project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/groups/', include('groups.urls')),
    path('api/roles/', include('roles.urls')),
    path('api/clients/', include('clients.urls')),
    path('api/permissions/', include('permissions.urls')),
]
