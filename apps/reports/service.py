from decimal import Decimal
from io import BytesIO

from django.utils import timezone
import nepali_datetime
from employees.models import Employee
from leaves.models import LeaveBalance, LeaveRequest, LeaveType
from reports.models import AuditLog, TaxSlab, logType
from core.models import SystemSettings
from attendance.models import DailyAttendance
from django.db.models import Model, Sum, Count, Q
from nepali_datetime import datetime
from hrm_project.utility import get_dates
from datetime import date
from weasyprint import HTML
from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType



class AuditLogService:
    def __init__(self, user):
        self.user = user

    def log(self, action: logType, instance : Model,  message: str = None, json_data: dict = None ):
        content_type = None
        object_id = None
        module_name = None
        user_obj = self.user if hasattr(self.user, 'is_authenticated') and self.user.is_authenticated else None
        if instance:
            content_type = ContentType.objects.get_for_model(instance)
            object_id = str(instance.pk)
            module_name = instance._meta.app_label
        return AuditLog.objects.create(
            user=user_obj,
            action=action,
            message=message,
            json_data=json_data,
            timestamp=timezone.now(),
            content_type=content_type,
            object_id=object_id,
            module_name=module_name,
        )
    
    def login(self, message: str = None, json_data: dict = None):
        return self.log(logType.LOGIN, instance=None, message=message, json_data=json_data)

    def logout(self, message: str = None, json_data: dict = None):
        return self.log(logType.LOGOUT, instance=None, message=message, json_data=json_data)

    def create(self, instance=None, message=None, json_data=None):
        return self.log(logType.CREATE, instance=instance, message=message, json_data=json_data)

    def update(self, instance=None, message=None, json_data=None):
        return self.log(logType.UPDATE, instance=instance, message=message, json_data=json_data)

    def delete(self, instance=None, message=None, json_data=None):
        return self.log(logType.DELETE, instance=instance, message=message, json_data=json_data)

    def email_sent(self, instance=None, message: str = None, json_data: dict = None):
        return self.log(logType.EMAIL_SENT, instance=instance, message=message, json_data=json_data)

    def report_generated(self, instance=None, message: str = None, json_data: dict = None):
        return self.log(logType.REPORT_GENERATED, instance=instance, message=message, json_data=json_data)
    
    
class ReportService:
    def __init__(self , employee):
        self.employee=employee
        dates=get_dates()
        self.start_date = date(2026, 5, 15)
        self.end_date = date(2026, 6, 15)
    
    def collecet_emp_data(emp_id):
        """ Collecet all data required for monthly report generation"""
        emp_data={}
        return emp_data
    
    def effective_working_days(self):
        """Returns total days present, late, or half day"""
        return DailyAttendance.objects.filter(
            employee=self.employee, 
            status__in=['PR', 'LT', 'HL'],
            date__range=(self.start_date,self.end_date)
            
        ).count()
        
    def is_new_joiner(self):
        from django.utils import timezone
        from datetime import timedelta
        print(self.employee.date_joined)
        if not self.employee.date_joined:
            return False
        return timezone.now() - self.employee.date_joined <= timedelta(days=30)
    
    def profile(self): # all working
        emp = self.employee
        settings = SystemSettings.get_settings()
        if self.employee.start_time and self.employee.end_time:
            shift_str = f"{self.employee.start_time.strftime('%H:%M')} - {self.employee.end_time.strftime('%H:%M')}"
        else:
            shift_str = f"{settings.office_start_time.strftime('%H:%M')} - {settings.office_end_time.strftime('%H:%M')}"
        return {
            "employee_id": emp.employee_id,
            "full_name": emp.get_full_name(),
            "department": emp.department.name if emp.department else None,
            "email": emp.email,
            "scheduled_shift": shift_str,
            "effective_working_days": self.effective_working_days(),
            "new_joiner": self.is_new_joiner(),
        }

    def attendance_summary(self): # NOTW : Woking

        qs = DailyAttendance.objects.filter(
            employee=self.employee,
            date__range=(self.start_date, self.end_date)
        )

        stats = qs.aggregate(
            total_days=Count('id'),
            days_present=Count('id', filter=Q(status__in=['PR', 'LT', 'HL'])),
            absent_days=Count('id', filter=Q(status='AB')),
            leave_days=Count('id', filter=Q(status='LV'))
        )
        
        # because LV is not marked manually by system when on leave so fall back to manual tracking 
        leave_days = stats['leave_days'] or 0
        if leave_days == 0:
            leave_days = LeaveRequest.objects.filter(
                employee=self.employee, 
                status="AP",
                start_date__range=(self.start_date, self.end_date)
            ).aggregate(total=Sum("total_days"))["total"] or 0

        total_days = stats['total_days'] or 0
        days_present = stats['days_present'] or 0
        absent_days = stats['absent_days'] or 0

        valid_qs = qs.filter(
            check_in_time__isnull=False,
            check_out_time__isnull=False
        )

        total_hours = valid_qs.aggregate(
            total=Sum("total_hours")
        )["total"] or 0

        valid_days = valid_qs.count()

        avg_hours = round(total_hours / valid_days, 2) if valid_days > 0 else 0.0


        attendance_percentage = round(
            (days_present / total_days) * 100, 2
        ) if total_days > 0 else 0.0

        return {
            "days_present": days_present,
            "total_days": total_days,
            "total_hours_worked": round(total_hours, 2),
            "average_hours_per_day": avg_hours,
            "approved_leave_days_taken": leave_days,
            "unpaid_absent_days": absent_days,
            "attendance_percentage": attendance_percentage
        }

    def voilation_summary(self): # all working
        qs = DailyAttendance.objects.filter(
        employee=self.employee,
        date__range=(self.start_date, self.end_date)
    )
        today = timezone.now().date()

        data = qs.aggregate(
            late_arrivals=Count("id", filter=Q(is_late=True)),
            early_departures=Count("id", filter=Q(is_early_departure=True)),
            short_hours_days=Count("id", filter=Q(total_hours__lte=7)),
            missing_checkouts=Count("id",filter=Q(check_out_time__isnull=True) & Q(date__lt=today)))

        data["three_late_arrivals"] = data["late_arrivals"] // 3

        return data
        
    def leave_balance_summary(self): # all working
        employee = self.employee
        from datetime import datetime as std_datetime
        current_year = std_datetime.now().year
        current_month = std_datetime.now().month

        result = {}

        leave_types = LeaveType.objects.filter(is_active=True)

        for lt in leave_types:
            balance = LeaveBalance.objects.filter(
                employee=employee,
                leave_type=lt,
                year=current_year
            ).first()

            allocated = balance.allocated if balance else lt.default_days
            
            # Calculate annual used 
            used_annual = LeaveRequest.objects.filter(
                employee=employee,
                leave_type=lt,
                status="AP",
                start_date__year=current_year
            ).aggregate(total=Sum("total_days"))["total"] or 0

            used_this_month = LeaveRequest.objects.filter(
                employee=employee,
                leave_type=lt,
                status="AP",
                start_date__month=current_month,
                start_date__year=current_year
            ).aggregate(total=Sum("total_days"))["total"] or 0

            result[lt.name] = {
                "allocated": allocated,
                "used": used_annual,
                "usedthismonth": used_this_month,
                "remain": allocated - used_annual
            }

        return result
        
    def approved_leaves(self): # all working
        leaves = LeaveRequest.objects.filter(
            employee=self.employee,
            status="AP",
            start_date__range=(self.start_date, self.end_date)
        ).select_related("leave_type")

        result = []
        for leave in leaves:
            result.append({
                "day": leave.start_date.day,
                "leave_type": leave.leave_type.name,
                "days": float(leave.total_days),
                "reason": leave.reason,
            })

        balances = LeaveBalance.objects.filter(
            employee=self.employee,
            year=self.start_date.year
        ).select_related("leave_type")

        summary = {}
        for b in balances:
            summary[b.leave_type.name] = {
                "used": float(b.used),
                "remaining": float(b.balance),
            }

        return {
            "logs": result,       
            "summary": summary,  
        }
    
    def attendanec_records(self):  # WORKING FINE 
        logs = DailyAttendance.objects.filter(
        employee=self.employee,
        date__range=(self.start_date, self.end_date)
    )

        result = []

        for log in logs:
            bs_date = nepali_datetime.date.from_datetime_date(log.date)
            result.append({
                "day": bs_date.day,
                "weekday": log.date.strftime("%A"),
                "check_in": log.check_in_time.strftime("%H:%M") if log.check_in_time else None,
                "check_out": log.check_out_time.strftime("%H:%M") if log.check_out_time else None,
                "hours": float(log.total_hours) if log.total_hours else 0,
                "status": log.get_status_display(),
                "notes": log.notes,
            })

        return sorted(result, key=lambda x: x["day"])

    def salary_calculation(self):
        # Convert Decimal basic_salary to float
        worked_days = int(self.attendance_summary()['days_present']) + int(self.attendance_summary()['approved_leave_days_taken'])
        violation_summary = self.voilation_summary()
        total_late = violation_summary['late_arrivals']
        three_late_arrivals = violation_summary['three_late_arrivals']
        total_absent = self.attendance_summary()['unpaid_absent_days']
        daily_rate = float(self.employee.basic_salary) / 24
        total_leave=len(self.approved_leaves()['logs'])

        earned_salary = worked_days * daily_rate

        late_penalty = total_late * (0.30 * daily_rate)
        three_late_penalty = three_late_arrivals * daily_rate

        if total_late == 0 and total_absent == 0 and total_leave== 0:
            bonus = 0.10 * earned_salary
        else:
            bonus = 0.0

        # Allowances
        allowance_amount = 0.0
        if getattr(self.employee, 'allowance', None):
            allowance_amount = float(self.employee.allowance.amount)

        # Tax
        tax_deduction = float((
            (
                TaxSlab.objects.get(
                    min_salary__lte=self.employee.basic_salary,
                    max_salary__gte=self.employee.basic_salary
                ).tax_rate
                if self.employee.basic_salary > 0
                else 0
            ) / Decimal(100)
        ) * self.employee.basic_salary)
                
        total_earnings = earned_salary + bonus + allowance_amount
        total_deductions = late_penalty + three_late_penalty + tax_deduction

        net_salary = total_earnings - total_deductions

        return {
            "earnings": {
                "base_salary": round(float(self.employee.basic_salary), 2),
                "earned_salary": round(earned_salary, 2),
                "bonus": round(bonus, 2),
                "allowance": round(allowance_amount, 2),
                "total_earnings": round(total_earnings, 2),
            },
            "deductions": {
                "late_penalty": round(late_penalty, 2),
                "three_late_penalty": round(three_late_penalty, 2),
                "tax_deduction": round(tax_deduction, 2),
                "total_deductions": round(total_deductions, 2),
            },
            "net_salary": round(net_salary, 2)
        }
        
    def render_pdf(self):
        template=get_template('reports/salary_report.html')
        context={
        "profile" : self.profile(),
        "attendance_summary" : self.attendance_summary(),
        "violation_summary" : self.voilation_summary(),
        "leave_balance" : self.leave_balance_summary(),
        "approved_leaves" : self.approved_leaves(),
        "attendance_logs" : self.attendanec_records(),
        "salary" : self.salary_calculation(),  
        }
        html_str=template.render(context)
        pdf_bytes = HTML(string=html_str).write_pdf()
        return pdf_bytes


    
    
    

        
        