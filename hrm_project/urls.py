"""
URL configuration for hrm_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('employees/', include('employees.web_urls')),
    path('attendance/', include('attendance.web_urls')),
    path('leaves/', include('leaves.web_urls')),
    path('biometric/', include('biometric.web_urls')),
    path('api/employees/', include('employees.urls')),
    path('api/attendance/', include('attendance.urls')),
    path('api/leaves/', include('leaves.urls')),
    path('api/biometric/', include('biometric.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
