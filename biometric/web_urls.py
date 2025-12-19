from django.urls import path
from . import web_views

urlpatterns = [
    path('test-connection/', web_views.test_device_connection, name='test_device_connection'),
    path('sync-attendance/', web_views.sync_attendance_data, name='sync_attendance_data'),
]
