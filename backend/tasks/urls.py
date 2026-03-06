from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, TaskTypeViewSet

router = DefaultRouter()
router.register(r'types', TaskTypeViewSet, basename='tasktype')
router.register(r'', TaskViewSet, basename='task')

urlpatterns = [
    path('', include(router.urls)),
]
