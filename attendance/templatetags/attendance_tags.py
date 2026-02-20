"""
Template tags for attendance calculations
"""
from django import template
from datetime import datetime, timedelta
from core.models import SystemSettings

register = template.Library()


@register.simple_tag
def is_late(check_in_time, date=None):
    """
    Check if a check-in time is late based on SystemSettings.
    
    Usage in template:
        {% load attendance_tags %}
        {% is_late record.check_in_time record.date as late %}
        {% if late %}LATE{% endif %}
    """
    if not check_in_time:
        return False
    
    try:
        settings = SystemSettings.get_settings()
        
        # If date is provided, use it; otherwise use today
        if date is None:
            from django.utils import timezone
            date = timezone.now().date()
        
        # Calculate grace time
        grace_time = datetime.combine(
            date,
            settings.office_start_time
        ) + timedelta(minutes=settings.late_threshold_minutes)
        
        # Convert check_in_time to datetime for comparison
        check_in_datetime = datetime.combine(date, check_in_time)
        
        return check_in_datetime > grace_time
    except:
        return False


@register.filter
def check_late(attendance_record):
    """
    Filter to check if an attendance record is late.
    
    Usage in template:
        {% load attendance_tags %}
        {% if record|check_late %}LATE{% endif %}
    """
    if not attendance_record or not attendance_record.check_in_time:
        return False
    
    return is_late(attendance_record.check_in_time, attendance_record.date)


@register.simple_tag
def get_grace_time():
    """
    Get the grace time from SystemSettings.
    
    Usage:
        {% load attendance_tags %}
        {% get_grace_time as grace %}
        Grace period: {{ grace }} minutes
    """
    try:
        settings = SystemSettings.get_settings()
        return settings.late_threshold_minutes
    except:
        return 15


@register.simple_tag
def get_office_start_time():
    """
    Get office start time from SystemSettings.
    
    Usage:
        {% load attendance_tags %}
        {% get_office_start_time as start_time %}
        Office starts at: {{ start_time }}
    """
    try:
        settings = SystemSettings.get_settings()
        return settings.office_start_time
    except:
        return "09:00:00"
