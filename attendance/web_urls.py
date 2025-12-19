from django.urls import path
from . import web_views

urlpatterns = [
    path('punch/', web_views.punch_attendance, name='punch_attendance'),
    path('my-attendance/', web_views.my_attendance, name='my_attendance'),
    path('report/', web_views.attendance_report, name='attendance_report'),
]
