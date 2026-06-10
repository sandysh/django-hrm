from django.utils import timezone
from reports.models import AuditLog, logType
from core.models import SystemSettings
from attendance.models import DailyAttendance
from django.db.models import Sum, Count, Q


class AuditLogService:
    
    def __init__(self, user):
        self.user = user

    def log(self, action: logType):
        user_obj = self.user if hasattr(self.user, 'is_authenticated') and self.user.is_authenticated else None
        return AuditLog.objects.create(
            user=user_obj,
            action=action,
            timestamp=timezone.now()
        )
        
    def login(self):
        return self.log(logType.LOGIN)

    def logout(self):
        return self.log(logType.LOGOUT)

    def create(self):
        return self.log(logType.CREATE)

    def update(self):
        return self.log(logType.UPDATE)

    def delete(self):
        return self.log(logType.DELETE)

    def email_sent(self):
        return self.log(logType.EMAIL_SENT)

    def report_generated(self):
        return self.log(logType.REPORT_GENERATED)
    
    
class ReportService:
    def __init__(self , employee):
        self.employee=employee
    
    def collecet_emp_data(emp_id):
        """ Collecet all data required for monthly report generation"""
        emp_data={}
        return emp_data
    
    def effective_working_days(self):
        """Returns total days present, late, or half day"""
        return DailyAttendance.objects.filter(
            employee=self.employee, 
            status__in=['PR', 'LT', 'HL']
        ).count()
        
    def is_new_joiner(self):
        from django.utils import timezone
        from datetime import timedelta
        if not self.employee.date_joined:
            return False
        return timezone.now() - self.employee.date_joined <= timedelta(days=30)
    
    def profile(self):
        emp = self.employee
        settings = SystemSettings.get_settings()
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
        
    def attendance_summary(self):
        # Aggregate all stats in a single query
        stats = DailyAttendance.objects.filter(employee=self.employee).aggregate(
            days_present=Count('id', filter=Q(status__in=['PR', 'LT', 'HL'])),
            leave_days=Count('id', filter=Q(status='LV')),
            absent_days=Count('id', filter=Q(status='AB')),
            total_hours=Sum('total_hours')
        )
        
        days_present = stats['days_present'] or 0
        total_hours = stats['total_hours'] or 0
        leave_days = stats['leave_days'] or 0
        absent_days = stats['absent_days'] or 0
        
        # Calculations
        avg_hours = round(float(total_hours) / days_present, 2) if days_present > 0 else 0.0
        
        # Total working days expected (assuming weekends/holidays are not in DailyAttendance unless marked as WO/HO)
        total_working_days = days_present + absent_days + leave_days
        
        attendance_percentage = round((days_present / total_working_days) * 100, 2) if total_working_days > 0 else 0.0
        
        return {
            "days_present": days_present,
            "total_hours_worked": total_hours,
            "average_hours_per_day": avg_hours,
            "approved_leave_days_taken": leave_days,
            "pure_leave_days": leave_days,
            "total_paid_days": days_present + leave_days,
            "attendance_percentage": attendance_percentage
        }
    
        
        


    
    
    

        
        