from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceRecordViewSet, DailyAttendanceViewSet

router = DefaultRouter()
router.register(r'records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'daily', DailyAttendanceViewSet, basename='daily-attendance')

urlpatterns = [
    path('', include(router.urls)),
]
