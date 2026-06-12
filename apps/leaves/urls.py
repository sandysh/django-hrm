from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaveTypeViewSet, LeaveRequestViewSet, HolidayViewSet, LeaveBalanceViewSet

router = DefaultRouter()
router.register(r'types', LeaveTypeViewSet, basename='leave-type')
router.register(r'requests', LeaveRequestViewSet, basename='leave-request')
router.register(r'holidays', HolidayViewSet, basename='holiday')
router.register(r'balances', LeaveBalanceViewSet, basename='leave-balance')

urlpatterns = [
    path('', include(router.urls)),
]
