"""
Views for system settings management.
"""
import json
from django.http import JsonResponse
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import TemplateView
from core.models import SystemSettings
from core.service import TaxSlabService
from reports.service import AuditLogService

class SuperAdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, 'Only superadmin can access settings')
        return redirect('dashboard')

class SettingsView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    """Unified settings page for all system configurations (superadmin only)."""
    template_name = 'systemsettings/settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from leaves.models import LeaveType
        context['system_settings'] = SystemSettings.get_settings()
        context['leave_types'] = LeaveType.objects.all().order_by('name')
        return context

    def post(self, request, *args, **kwargs):
        system_settings = SystemSettings.get_settings()
        if 'update_office_hours' in request.POST:
            try:
                system_settings.office_start_time = request.POST.get('office_start_time')
                system_settings.office_end_time = request.POST.get('office_end_time')
                system_settings.late_threshold_minutes = int(request.POST.get('late_threshold_minutes', 15))
                system_settings.save()
                
                AuditLogService(request.user).update(
                    instance=system_settings,
                    message="Updated office hours settings",
                    json_data={
                        "office_start_time": str(system_settings.office_start_time),
                        "office_end_time": str(system_settings.office_end_time),
                        "late_threshold_minutes": system_settings.late_threshold_minutes
                    }
                )
                
                messages.success(request, 'Office hours updated successfully!')
                return redirect('settings')
            except Exception as e:
                messages.error(request, f'Error updating office hours: {str(e)}')
        
        return self.render_to_response(self.get_context_data())

class SystemSettingsView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = 'systemsettings/system_settings.html'

    def get_context_data(self):
        context = super().get_context_data()
        context['system_settings'] = SystemSettings.get_settings()
        return context

class AllowanceSettingsView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = 'systemsettings/allowance_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.service import AllowanceService
        allowances = AllowanceService.get_all_allows()
        context['allowances'] = allowances
        total_amount = sum([a.amount for a in allowances])
        context['total_allowance_amount'] = total_amount
        context['avg_allowance_amount'] = round(total_amount / len(allowances), 2) if allowances else 0
        return context

    def post(self, request, *args, **kwargs):
        from core.service import AllowanceService
        try:
            name = request.POST.get('name')
            amount = int(request.POST.get('amount', 0))
            allowance = AllowanceService.create_allow(name, amount)
            AuditLogService(request.user).create(
                instance=allowance,
                message=f"Created allowance {name}",
                json_data={"allowance_id": allowance.id, "name": name, "amount": amount}
            )
            messages.success(request, 'Allowance created successfully!')
        except Exception as e:
            messages.error(request, f'Failed to create allowance: {str(e)}')
            
        return redirect('allowance_settings')

    def put(self, request, *args, **kwargs):
        try:
            from core.service import AllowanceService
            data = json.loads(request.body)
            allowance_id = data.get('allowance_id')
            if not allowance_id:
                return JsonResponse({'success': False, 'message': 'No allowance_id provided.'}, status=400)
            
            update_data = {}
            if 'name' in data: update_data['name'] = data['name']
            if 'amount' in data: update_data['amount'] = int(data['amount'])
                
            allow = AllowanceService.update_allow(int(allowance_id), **update_data)
            if allow:
                AuditLogService(request.user).update(
                    instance=allow,
                    message=f"Updated allowance ID {allowance_id}",
                    json_data={"allowance_id": allowance_id, "updated_fields": update_data}
                )
                return JsonResponse({'success': True, 'message': 'Allowance updated successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to update allowance.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            from core.service import AllowanceService
            data = json.loads(request.body)
            allowance_id = data.get('allowance_id')
            if allowance_id:
                success = AllowanceService.delete_allow(int(allowance_id))
                if success:
                    AuditLogService(request.user).delete(
                        instance=None, # Already deleted
                        message=f"Deleted allowance ID {allowance_id}",
                        json_data={"allowance_id": allowance_id}
                    )
                    return JsonResponse({'success': True, 'message': 'Allowance deleted successfully!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to delete allowance.'}, status=400)
            return JsonResponse({'success': False, 'message': 'No allowance_id provided.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

class FundSettingsView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = 'systemsettings/fund_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.service import FundService
        funds = FundService.get_all_funds()
        context['fund_types'] = funds
        
        context['total_emp_contribution'] = sum([f.emp_contribution for f in funds])
        context['total_org_contribution'] = sum([f.org_contribution for f in funds])
        context['enrolled_employees_count'] = sum([f.employee_count for f in funds])
        return context

    def post(self, request, *args, **kwargs):
        from core.service import FundService
        try:
            name = request.POST.get('name')
            emp_contribution = int(request.POST.get('emp_contribution', 0))
            org_contribution = int(request.POST.get('org_contribution', 0))
            fund = FundService.create_fund(name, emp_contribution, org_contribution)
            AuditLogService(request.user).create(
                instance=fund,
                message=f"Created fund type {name}",
                json_data={"fund_id": fund.id, "name": name, "emp_contribution": emp_contribution, "org_contribution": org_contribution}
            )
            messages.success(request, 'Fund type created successfully!')
        except Exception as e:
            messages.error(request, f'Failed to create fund type: {str(e)}')
            
        return redirect('fund_settings')

    def put(self, request, *args, **kwargs):
        try:
            from core.service import FundService
            data = json.loads(request.body)
            fund_id = data.get('fund_id')
            if not fund_id:
                return JsonResponse({'success': False, 'message': 'No fund_id provided.'}, status=400)
            
            update_data = {}
            if 'name' in data: update_data['name'] = data['name']
            if 'emp_contribution' in data: update_data['emp_contribution'] = int(data['emp_contribution'])
            if 'org_contribution' in data: update_data['org_contribution'] = int(data['org_contribution'])
                
            fund = FundService.update_fund(int(fund_id), **update_data)
            if fund:
                AuditLogService(request.user).update(
                    instance=fund,
                    message=f"Updated fund type ID {fund_id}",
                    json_data={"fund_id": fund_id, "updated_fields": update_data}
                )
                return JsonResponse({'success': True, 'message': 'Fund type updated successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to update fund type.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            from core.service import FundService
            data = json.loads(request.body)
            fund_id = data.get('fund_id')
            if fund_id:
                success = FundService.delete_fund(int(fund_id))
                if success:
                    AuditLogService(request.user).delete(
                        instance=None, # Already deleted
                        message=f"Deleted fund type ID {fund_id}",
                        json_data={"fund_id": fund_id}
                    )
                    return JsonResponse({'success': True, 'message': 'Fund type deleted successfully!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to delete fund type.'}, status=400)
            return JsonResponse({'success': False, 'message': 'No fund_id provided.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

class TaxSettingsView(LoginRequiredMixin, SuperAdminRequiredMixin, TemplateView):
    template_name = 'systemsettings/tax_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from core.service import TaxSlabService, FiscalYearService
        context['tax_slabs'] = TaxSlabService.get_all_slabs()
        context['fiscal_years'] = FiscalYearService.get_all_fys()
        return context

    def post(self, request, *args, **kwargs):
        from core.service import TaxSlabService, FiscalYearService
        from reports.models import FiscalYear
        try:
            name = request.POST.get('name')
            min_salary = float(request.POST.get('min_salary', 0))
            max_salary_str = request.POST.get('max_salary')
            max_salary = float(max_salary_str) if max_salary_str else 9999999999.0
            tax_rate = int(request.POST.get('tax_rate', 0))
            
            fy_start_date = request.POST.get('fy_start_date')
            fy_end_date = request.POST.get('fy_end_date')

            if not fy_start_date or not fy_end_date:
                raise ValueError("Fiscal Year Start and End dates are required.")

            fy = FiscalYear.objects.filter(start_date=fy_start_date, end_date=fy_end_date).first()
            if not fy:
                # Create a new active fiscal year if it doesn't exist
                fy = FiscalYearService.create_fy(fy_start_date, fy_end_date, True)
                AuditLogService(request.user).create(
                    instance=fy,
                    message=f"Created fiscal year FY {fy.start_date} to {fy.end_date}",
                    json_data={"fy_id": fy.id, "start_date": str(fy.start_date), "end_date": str(fy.end_date)}
                )
            
            slab = TaxSlabService.create_slab(name, min_salary, max_salary, tax_rate, fy)
            AuditLogService(request.user).create(
                instance=slab,
                message=f"Created tax slab {name}",
                json_data={"slab_id": slab.id, "name": name, "min_salary": min_salary, "max_salary": max_salary, "tax_rate": tax_rate, "fy_id": fy.id}
            )
            messages.success(request, 'Tax slab created successfully!')
        except Exception as e:
            messages.error(request, f'Failed to create: {str(e)}')
            
        return redirect('tax_settings')

    def put(self, request, *args, **kwargs):
        try:
            from core.service import TaxSlabService, FiscalYearService
            from reports.models import FiscalYear
            data = json.loads(request.body)
            slab_id = data.get('slab_id')
            if not slab_id:
                return JsonResponse({'success': False, 'message': 'No slab_id provided.'}, status=400)
            
            update_data = {}
            if 'name' in data: update_data['name'] = data['name']
            if 'min_salary' in data: update_data['min_salary'] = float(data['min_salary'])
            if 'max_salary' in data: 
                val = data['max_salary']
                update_data['max_salary'] = float(val) if val else 9999999999.0
            if 'tax_rate' in data: update_data['tax_rate'] = int(data['tax_rate'])
            
            if 'fy_start_date' in data and 'fy_end_date' in data:
                fy_start_date = data['fy_start_date']
                fy_end_date = data['fy_end_date']
                if fy_start_date and fy_end_date:
                    fy = FiscalYear.objects.filter(start_date=fy_start_date, end_date=fy_end_date).first()
                    if not fy:
                        fy = FiscalYearService.create_fy(fy_start_date, fy_end_date, True)
                        AuditLogService(request.user).create(
                            instance=fy,
                            message=f"Created fiscal year FY {fy.start_date} to {fy.end_date}",
                            json_data={"fy_id": fy.id, "start_date": str(fy.start_date), "end_date": str(fy.end_date)}
                        )
                    update_data['fiscal_year'] = fy
                
            slab = TaxSlabService.update_slab(int(slab_id), **update_data)
            if slab:
                AuditLogService(request.user).update(
                    instance=slab,
                    message=f"Updated tax slab ID {slab_id}",
                    json_data={"slab_id": slab_id, "updated_fields": update_data if not 'fiscal_year' in update_data else {k: v.id if k == 'fiscal_year' else v for k, v in update_data.items()}}
                )
                return JsonResponse({'success': True, 'message': 'Tax slab updated successfully!'})
            else:
                return JsonResponse({'success': False, 'message': 'Failed to update tax slab.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)

    def delete(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            slab_id = data.get('slab_id')
            if slab_id:
                success = TaxSlabService.delete_slab(int(slab_id))
                if success:
                    AuditLogService(request.user).delete(
                        instance=None, # Already deleted
                        message=f"Deleted tax slab ID {slab_id}",
                        json_data={"slab_id": slab_id}
                    )
                    return JsonResponse({'success': True, 'message': 'Tax slab deleted successfully!'})
                else:
                    return JsonResponse({'success': False, 'message': 'Failed to delete tax slab.'}, status=400)
            return JsonResponse({'success': False, 'message': 'No slab_id provided.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
