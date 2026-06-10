
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_mail(reciver_email, template, context_data):
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
        
        html_message = render_to_string(template, context_data)
        
        subject = context_data.get('subject', 'HRM Notification')
        
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.EMAIL_HOST_USER,
            to=[reciver_email],
        )
        
        email.content_subtype = 'html'

        email.send(fail_silently=False)
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {reciver_email}: {str(e)}")
        return False

    