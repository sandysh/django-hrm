from django.views import View 
from django.views.generic import ListView , TemplateView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from hrm_project.utility import get_dates
from reports.service import ReportService
from .models import AuditLog, logType
from django.db.models import Q
from employees.models import Employee

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Payroll
from django.http import HttpResponse


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
        action_type = request.POST.get('action_type')
        emp_id = self.kwargs.get('emp_id')
        employee = get_object_or_404(Employee, id=emp_id)
        
        if action_type == 'save':
            dates = get_dates()
            payroll_date = dates['start_ad']
            defaults = {
                'effective_working_days': int(float(request.POST.get('effective_working_days', 0))),
                'days_present': int(float(request.POST.get('days_present', 0))),
                'total_hours_worked': float(request.POST.get('total_hours_worked', 0)),
                'leave_days_taken': int(float(request.POST.get('leave_days_taken', 0))),
                'unpaid_absent_days': int(float(request.POST.get('unpaid_absent_days', 0))),
                'late_arrivals': int(float(request.POST.get('late_arrivals', 0))),
                'early_departures': int(float(request.POST.get('early_departures', 0))),
                'missing_checkouts': int(float(request.POST.get('missing_checkouts', 0))),
                'three_late_arrivals': int(float(request.POST.get('three_late_arrivals', 0))),
                'base_salary': request.POST.get('base_salary', 0) or 0,
                'earned_salary': request.POST.get('earned_salary', 0) or 0,
                'bonus': request.POST.get('bonus', 0) or 0,
                'allowance': request.POST.get('allowance', 0) or 0,
                'total_earnings': request.POST.get('total_earnings', 0) or 0,
                'late_penalty': request.POST.get('late_penalty', 0) or 0,
                'three_late_penalty': request.POST.get('three_late_penalty', 0) or 0,
                'tax_deduction': request.POST.get('tax_deduction', 0) or 0,
                'total_payable': request.POST.get('total_payable', 0) or 0,
                'fine_deduction': request.POST.get('fine_deduction', 0) or 0,
            }
            try:
                Payroll.objects.update_or_create(
                    employee=employee,
                    date=payroll_date,
                    defaults=defaults
                )
                messages.success(request, f'Report data for {employee.get_full_name()} approved and saved successfully.')
            except Exception as e:
                messages.error(request, f'Error saving payroll data: {e}')
            return redirect('employee_report_data', emp_id=emp_id)
            
        elif action_type == 'delete':
            try:
                payroll = Payroll.objects.filter(employee=employee).first()
                if payroll:
                    payroll.delete()
                    messages.success(request, f'Report data for {employee.get_full_name()} deleted successfully.')
            except Exception as e:
                messages.error(request, f'Error deleting payroll data: {e}')
            return redirect('employee_report_data', emp_id=emp_id)
            
        elif action_type == 'download':
            service = ReportService(employee=employee)
            pdf = service.render_pdf()
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="salary_report_{employee.employee_id}.pdf"'
            return response
            
        elif action_type == 'mail':
            # TODO: Implement actual Email sending logic here using django.core.mail
            messages.success(request, f'Report data for {employee.get_full_name()} has been emailed successfully.')
            return redirect('employee_report_data', emp_id=emp_id)

        return redirect('employee_list')