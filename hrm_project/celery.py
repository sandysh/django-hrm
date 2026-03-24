"""
Celery configuration for hrm_project.
"""
import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_project.settings')

app = Celery('hrm_project')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule
app.conf.beat_schedule = {
    # Auto-sync today's attendance from the biometric device every 5 minutes
    'sync-todays-attendance-every-5-minutes': {
        'task': 'biometric.tasks.sync_attendance_from_device',
        'schedule': crontab(minute='*/5'),
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
