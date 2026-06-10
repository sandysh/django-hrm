
from datetime import time, timedelta

from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging
from celery import shared_task
from django.utils import timezone

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
    from employees.models import Employee
    from attendance.models import DailyAttendance
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
    

    