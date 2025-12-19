from django.db import models


class SystemSettings(models.Model):
    """
    System-wide settings for the HRM application.
    Only one instance should exist.
    """
    # Office Hours
    office_start_time = models.TimeField(default='09:00:00', help_text="Office start time (e.g., 09:00)")
    office_end_time = models.TimeField(default='17:00:00', help_text="Office end time (e.g., 17:00)")
    late_threshold_minutes = models.IntegerField(default=15, help_text="Minutes after start time to mark as late")
    
    # Working Days
    working_days = models.CharField(
        max_length=50,
        default='1,2,3,4,5',
        help_text="Comma-separated weekday numbers (0=Monday, 6=Sunday)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'system_settings'
        verbose_name = 'System Settings'
        verbose_name_plural = 'System Settings'
    
    def __str__(self):
        return f"System Settings (Office: {self.office_start_time} - {self.office_end_time})"
    
    @classmethod
    def get_settings(cls):
        """Get or create the singleton settings instance."""
        settings, created = cls.objects.get_or_create(pk=1)
        return settings
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists."""
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Prevent deletion of settings."""
        pass
