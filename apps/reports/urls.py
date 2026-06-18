from django.urls import path
from . import views

urlpatterns = [
    path('audit-logs/', views.AuditLogListView.as_view(), name='audit_log_list'),
    path('test-render/', views.ReportView.as_view(), name='testrender'),
    path('employee/<int:emp_id>/', views.EmployeeReportDataView.as_view(), name='employee_report_data'),
]
