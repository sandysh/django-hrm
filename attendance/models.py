from django.db import models
from employees.models import Employee


class AttendanceRecord(models.Model):
    """
    Model to store attendance records from biometric device.
    """
    PUNCH_TYPE_CHOICES = [
        ('IN', 'Check In'),
        ('OUT', 'Check Out'),
        ('BREAK_OUT', 'Break Out'),
        ('BREAK_IN', 'Break In'),
    ]
    
    STATUS_CHOICES = [
        ('PR', 'Present'),
        ('AB', 'Absent'),
        ('HL', 'Half Day'),
        ('LT', 'Late'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='attendance_records')
    punch_time = models.DateTimeField(db_index=True)
    punch_type = models.CharField(max_length=10, choices=PUNCH_TYPE_CHOICES, default='IN')
    
    # Biometric device information
    biometric_user_id = models.IntegerField(help_text="UID from biometric device")
    device_id = models.CharField(max_length=50, blank=True, help_text="Device serial number")
    punch_state = models.IntegerField(null=True, blank=True, help_text="Punch state from device")
    verify_type = models.IntegerField(null=True, blank=True, help_text="Verification type from device")
    
    # Metadata
    synced_at = models.DateTimeField(auto_now_add=True)
    is_manual = models.BooleanField(default=False, help_text="Manually added record")
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'attendance_records'
        ordering = ['-punch_time']
        unique_together = ['employee', 'punch_time', 'punch_type']
        indexes = [
            models.Index(fields=['employee', 'punch_time']),
            models.Index(fields=['punch_time']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.punch_time} ({self.punch_type})"


class DailyAttendance(models.Model):
    """
    Aggregated daily attendance summary.
    """
    STATUS_CHOICES = [
        ('PR', 'Present'),
        ('AB', 'Absent'),
        ('HL', 'Half Day'),
        ('LT', 'Late'),
        ('LV', 'On Leave'),
        ('WO', 'Week Off'),
        ('HO', 'Holiday'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='daily_attendance')
    date = models.DateField(db_index=True)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES, default='AB')
    
    # Time tracking
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Break time
    total_break_time = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                          help_text="Total break time in hours")
    
    # Flags
    is_late = models.BooleanField(default=False)
    is_early_departure = models.BooleanField(default=False)
    is_overtime = models.BooleanField(default=False)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'daily_attendance'
        ordering = ['-date']
        unique_together = ['employee', 'date']
        indexes = [
            models.Index(fields=['employee', 'date']),
            models.Index(fields=['date', 'status']),
        ]
    
    def __str__(self):
        return f"{self.employee.employee_id} - {self.date} ({self.status})"


class AttendanceSettings(models.Model):
    """
    Global attendance settings.
    """
    # Working hours
    standard_work_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    grace_period_minutes = models.IntegerField(default=15, help_text="Grace period for late arrival")
    
    # Shift timings
    shift_start_time = models.TimeField(default='09:00:00')
    shift_end_time = models.TimeField(default='17:00:00')
    
    # Break settings
    lunch_break_duration = models.IntegerField(default=60, help_text="Lunch break in minutes")
    
    # Overtime
    overtime_threshold_hours = models.DecimalField(max_digits=4, decimal_places=2, default=8.00)
    
    # Half day threshold
    half_day_threshold_hours = models.DecimalField(max_digits=4, decimal_places=2, default=4.00)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'attendance_settings'
        verbose_name = 'Attendance Settings'
        verbose_name_plural = 'Attendance Settings'
    
    def __str__(self):
        return f"Attendance Settings (Updated: {self.updated_at})"



