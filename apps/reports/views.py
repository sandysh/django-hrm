from django.views import View 
from django.views.generic import ListView , TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from reports.service import ReportService
from .models import AuditLog, logType
from django.db.models import Q
from employees.models import Employee

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payroll


#logger config
import logging
logger=logging.getLogger(__name__)

class AuditLogListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = AuditLog
    template_name = 'reports/audit_log_list.html'
    context_object_name = 'logs'
    paginate_by = 20

    def test_func(self):
        return self.request.user.is_staff

    def get_queryset(self):
        queryset = AuditLog.objects.select_related('user').order_by('-timestamp')
        
        search = self.request.GET.get('search')
        action = self.request.GET.get('action')
        
        if search:
            queryset = queryset.filter(
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search) |
                Q(user__username__icontains=search) |
                Q(user__employee_id__icontains=search)
            )
            
        if action:
            queryset = queryset.filter(action=action)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        context['action_filter'] = self.request.GET.get('action', '')
        context['log_types'] = logType.choices
        return context

class ReportView(LoginRequiredMixin, TemplateView):
    template_name='reports/salary_report.html'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = super().get_context_data(**kwargs)

        employee = Employee.objects.get(employee_id="EMP114")   
        
        service = ReportService(
            employee=employee,
        )

        context["profile"] = service.profile()
        context["attendance_summary"] = service.attendance_summary()
        context["violation_summary"] = service.voilation_summary()
        context["leave_balance"] = service.leave_balance_summary()
        context["approved_leaves"] = service.approved_leaves()
        context["attendance_logs"] = service.attendanec_records()
        context["salary"] = service.salary_calculation()

        return context

class EmployeeReportDataView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'reports/generate_report_form.html'
    
    def test_func(self):
        return self.request.user.is_staff
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        emp_id = self.kwargs.get('emp_id')
        employee = get_object_or_404(Employee, id=emp_id)
        service = ReportService(employee=employee)
        
        context["employee"] = employee
        context["profile"] = service.profile()
        context["attendance_summary"] = service.attendance_summary()
        context["violation_summary"] = service.voilation_summary()
        context["leave_balance"] = service.leave_balance_summary()
        context["approved_leaves"] = service.approved_leaves()
        context["attendance_logs"] = service.attendanec_records()
        context["salary"] = service.salary_calculation()
        
        existing_payroll = Payroll.objects.filter(employee=employee).first()
        context["existing_payroll"] = existing_payroll
        
        return context

    def post(self, request, *args, **kwargs):
        emp_id = self.kwargs.get('emp_id')
        employee = get_object_or_404(Employee, id=emp_id)
        
        total_payable = request.POST.get('total_payable', 0)
        fine_deduction = request.POST.get('fine_deduction', 0)
        messages.success(request, f'Report data for {employee.get_full_name()} approved and saved successfully.')
        return redirect('employee_list')
    
    