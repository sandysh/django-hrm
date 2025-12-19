from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceRecordViewSet, DailyAttendanceViewSet, AttendanceSettingsViewSet

router = DefaultRouter()
router.register(r'records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'daily', DailyAttendanceViewSet, basename='daily-attendance')
router.register(r'settings', AttendanceSettingsViewSet, basename='attendance-settings')

urlpatterns = [
    path('', include(router.urls)),
]
