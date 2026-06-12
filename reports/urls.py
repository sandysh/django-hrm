from django.urls import path
from . import views

urlpatterns = [
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
    path('mail/', views.MailView.as_view(), name='mail'),
    path('test-render/', views.ReportView.as_view(), name='testrender'),
]
