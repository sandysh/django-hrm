from django.db import models


class BiometricDevice(models.Model):
    """
    Model to store biometric device information.
    """
    name = models.CharField(max_length=100)
    ip_address = models.GenericIPAddressField(unique=True)
    port = models.IntegerField(default=4370)
    password = models.IntegerField(default=0)
    timeout = models.IntegerField(default=5, help_text="Connection timeout in seconds")
    
    serial_number = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    platform = models.CharField(max_length=50, blank=True)
    device_name = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    last_sync_time = models.DateTimeField(null=True, blank=True)
    last_connection_status = models.BooleanField(default=False)
    last_error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'biometric_devices'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.ip_address})"


class SyncLog(models.Model):
    """
    Log of synchronization activities with biometric device.
    """
    SYNC_TYPE_CHOICES = [
        ('USER_PUSH', 'User Push to Device'),
        ('USER_PULL', 'User Pull from Device'),
        ('ATTENDANCE_PULL', 'Attendance Pull from Device'),
        ('DEVICE_INFO', 'Device Info Fetch'),
    ]
    
    STATUS_CHOICES = [
        ('SU', 'Success'),
        ('FA', 'Failed'),
        ('PA', 'Partial'),
    ]
    
    device = models.ForeignKey(BiometricDevice, on_delete=models.CASCADE, 
                              related_name='sync_logs', null=True, blank=True)
    sync_type = models.CharField(max_length=20, choices=SYNC_TYPE_CHOICES)
    status = models.CharField(max_length=2, choices=STATUS_CHOICES)
    
    records_processed = models.IntegerField(default=0)
    records_success = models.IntegerField(default=0)
    records_failed = models.IntegerField(default=0)
    
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    error_message = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    
    class Meta:
        db_table = 'sync_logs'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['sync_type', 'status']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.sync_type} - {self.status} ({self.started_at})"
