from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BiometricDeviceViewSet, SyncLogViewSet

router = DefaultRouter()
router.register(r'devices', BiometricDeviceViewSet, basename='biometric-device')
router.register(r'sync-logs', SyncLogViewSet, basename='sync-log')

urlpatterns = [
    path('', include(router.urls)),
]
