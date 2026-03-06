from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClientViewSet, ClientStatusViewSet

router = DefaultRouter()
router.register(r'statuses', ClientStatusViewSet, basename='clientstatus')
router.register(r'', ClientViewSet, basename='client')

urlpatterns = [
    path('', include(router.urls)),
]
