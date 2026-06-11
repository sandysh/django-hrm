
from datetime import time, timedelta

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging
from celery import shared_task
from django.utils import timezone
from employees.models import Employee
from attendance.models import DailyAttendance
import nepali_datetime
import datetime
from django.db.models import Q , Count , Sum 
from hrm_project.utility import get_dates
from reports.service import ReportService

logger = logging.getLogger(__name__)

@shared_task
def send_email(reciver_email, template, context_data):
    """
    Send an email using a Django template.
    
    Args:
        reciver_email (str): Email address of the recipient
        template (str): Path to the email template (e.g., 'emails/punch_in_missing.html')
        context_data (dict): Context data to render in the template
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Log all email details
        logger.info("=" * 50)
        logger.info(f"RECIPIENT: {reciver_email}")
        logger.info(f"TEMPLATE: {template}")
        logger.info(f"CONTEXT: {context_data}")
        
        html_message = render_to_string(template, context_data)
        subject = context_data.get('subject', 'HRM Notification')
        
        logger.info(f"SUBJECT: {subject}")
        logger.info(f"HTML MESSAGE LENGTH: {len(html_message)} chars")
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[reciver_email],
        )
        email.content_subtype = 'html'
        
        result = email.send(fail_silently=False)
        logger.info(f"EMAIL SENT RESULT: {result}")
        logger.info("=" * 50)
        return True
        
    except Exception as e:
        logger.error(f"EMAIL FAILED: {str(e)}", exc_info=True)
        return False
    
    
@shared_task
def send_reminder():
    """send reminder for employee who have not punched in or are late """
    not_punched_users=DailyAttendance.objects.filter(
        date=timezone.now().date(),
        check_in_time__gte=time(10, 10)
    )
    for employee_record in not_punched_users:
        print(employee_record.employee)
        print(employee_record.employee.email)
        context = {
            "today": timezone.now().date().strftime("%Y-%m-%d"),
            "employee_name": employee_record.employee.username,
            "employee_id": employee_record.employee.employee_id,
            "department": employee_record.employee.department.name if employee_record.employee and employee_record.employee.department else "Game Devlopment",
            "regularization_deadline": (
                timezone.now().date() + timedelta(days=2)
            ).strftime("%Y-%m-%d"),
        }

        send_email.delay(
            employee_record.employee.email,
            "emails/punch_in_missing.html",
            context,
        )
        
        
           
@shared_task
def send_punch_out_reminder():
    """send reminder for employee who have not punched out """
    not_punched_users=DailyAttendance.objects.filter(
        date=timezone.now().date(),
        check_out_time__isnull=True
    )
    for employee_record in not_punched_users:
        context = {
            "today": timezone.now().date().strftime("%Y-%m-%d"),
            "employee_name": employee_record.employee.username,
            "employee_id": employee_record.employee.employee_id,
            "department": employee_record.employee.department.name if employee_record.employee and employee_record.employee.department else "Game Devlopment",
            "regularization_deadline": (
                timezone.now().date() + timedelta(days=2)
            ).strftime("%Y-%m-%d"),
        }

        send_email.delay(
            employee_record.employee.email,
            "emails/punch_out_missing.html",
            context,
        )
        
@shared_task
def send_payroll_notice():
    """ Send payroll generation email to employees at end of each nepali month. """
    # today_ad = datetime.date.today()
    # today_bs = nepali_datetime.date.from_datetime_date(today_ad)

    # if today_bs.month == 12:
    #     next_month = nepali_datetime.date(today_bs.year + 1, 1, 1)
    # else:
    #     next_month = nepali_datetime.date(today_bs.year, today_bs.month + 1, 1)

    # last_day = next_month - datetime.timedelta(days=1)
    
    # if today_bs==last_day:
    
    dates=get_dates()
    if dates['today_bs']==dates['end_bs']:
       emps=Employee.objects.all()
       context={}
       for emp in emps:
        service = ReportService(
            employee=emp,
        )
        
        context["profile"] = service.profile()
        context["attendance_summary"] = service.attendance_summary()
        context["violation_summary"] = service.voilation_summary()
        context["leave_balance"] = service.leave_balance_summary()
        context["approved_leaves"] = service.approved_leaves()
        context["attendance_logs"] = service.attendanec_records()
        context["salary"] = service.salary_calculation()
        
        
def create_latesummary_roll(start_date,end_date):
    user=Employee.objects.all().first()
    qs=DailyAttendance.objects.filter(
        employee=user,
        date__range=(start_date,end_date)
    )
    data=qs.aggregate(
        late_arrival=Count("id",filter=Q(is_late=True)),
        early_departures=Count("id", filter=Q(is_early_departure=True)),
        short_hours_days=Count("id", filter=Q(total_hours__lt=1.5)),
    )
    
    missing_checkouts = qs.filter(check_out_time__isnull=True).count()
    three_late_arrivals=qs.filter(is_late=True).count()//3
    
    data[missing_checkouts]=missing_checkouts
    # TODO : Ask how monthly pas is calculated 
    return data

    
    
    