from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoleViewSet, RolePermissionViewSet

router = DefaultRouter()
router.register(r'', RoleViewSet, basename='role')
router.register(r'permissions', RolePermissionViewSet, basename='role-permission')

urlpatterns = [
    path('', include(router.urls)),
]
