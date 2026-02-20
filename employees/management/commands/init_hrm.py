"""
Management command to initialize the HRM system with sample data.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from employees.models import Employee
from leaves.models import LeaveType, LeaveBalance
from core.models import SystemSettings
from biometric.models import BiometricDevice


class Command(BaseCommand):
    help = 'Initialize HRM system with default data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Initializing HRM system...'))
        
        # Create Attendance Settings
        self.create_attendance_settings()
        
        # Create Leave Types
        self.create_leave_types()
        
        # Create Biometric Device
        self.create_biometric_device()
        
        self.stdout.write(self.style.SUCCESS('✓ HRM system initialized successfully!'))
    
    def create_attendance_settings(self):
        """Create default system settings."""
        settings = SystemSettings.get_settings()
        if settings.id:
            self.stdout.write(self.style.WARNING('  System settings already exist'))
        else:
            self.stdout.write(self.style.SUCCESS('  ✓ Created system settings'))
    
    def create_leave_types(self):
        """Create default leave types."""
        leave_types = [
            {
                'name': 'Annual Leave',
                'code': 'AL',
                'description': 'Annual vacation leave',
                'default_days': 15,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Sick Leave',
                'code': 'SL',
                'description': 'Medical/sick leave',
                'default_days': 10,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Casual Leave',
                'code': 'CL',
                'description': 'Casual/personal leave',
                'default_days': 5,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Unpaid Leave',
                'code': 'UL',
                'description': 'Leave without pay',
                'default_days': 0,
                'is_paid': False,
                'requires_approval': True,
            },
            {
                'name': 'Maternity Leave',
                'code': 'ML',
                'description': 'Maternity leave for female employees',
                'default_days': 90,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Paternity Leave',
                'code': 'PL',
                'description': 'Paternity leave for male employees',
                'default_days': 7,
                'is_paid': True,
                'requires_approval': True,
            },
        ]
        
        created_count = 0
        for lt_data in leave_types:
            lt, created = LeaveType.objects.get_or_create(
                code=lt_data['code'],
                defaults=lt_data
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created_count} leave types'))
    
    def create_biometric_device(self):
        """Create default biometric device configuration."""
        device, created = BiometricDevice.objects.get_or_create(
            ip_address='192.168.1.201',
            defaults={
                'name': 'Main Office Biometric Device',
                'port': 4370,
                'password': 0,
                'timeout': 5,
                'is_active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('  ✓ Created biometric device configuration'))
        else:
            self.stdout.write(self.style.WARNING('  Biometric device already exists'))
