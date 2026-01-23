from django.urls import path
from .views import get_available_permissions

urlpatterns = [
    path('available/', get_available_permissions, name='available-permissions'),
]
