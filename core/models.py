from django.db import models


class SystemSettings(models.Model):
    """
    System-wide settings for the HRM application.
    Consolidated all attendance and office settings.
    Only one instance should exist.
    
    Core settings use typed fields for validation and type safety.
    Additional settings can be stored in the 'additional_settings' JSON field.
    """
    # Office Hours (Core Settings - Typed)
    office_start_time = models.TimeField(default='09:00:00', help_text="Office start time (e.g., 09:00)")
    office_end_time = models.TimeField(default='17:00:00', help_text="Office end time (e.g., 17:00)")
    late_threshold_minutes = models.IntegerField(default=15, help_text="Minutes after start time to mark as late")
    
    # Working Hours & Thresholds (Core Settings - Typed)
    standard_work_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=8.00,
        help_text="Standard working hours per day"
    )
    overtime_threshold_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=8.00,
        help_text="Hours threshold for overtime calculation"
    )
    half_day_threshold_hours = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=4.00,
        help_text="Minimum hours for half-day attendance"
    )
    
    # Break Settings (Core Settings - Typed)
    lunch_break_duration = models.IntegerField(
        default=60, 
        help_text="Lunch break duration in minutes"
    )
    
    # Working Days (Core Settings - Typed)
    working_days = models.CharField(
        max_length=50,
        default='1,2,3,4,5',
        help_text="Comma-separated weekday numbers (0=Monday, 6=Sunday)"
    )
    
    # Flexible Additional Settings (JSON - No migrations needed for new settings)
    additional_settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional settings in key-value format. Add new settings here without migrations."
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

    def get_additional_setting(self, key, default=None):
        """
        Get a value from additional_settings.
        
        Usage:
            settings.get_additional_setting('email_notifications', True)
            settings.get_additional_setting('max_login_attempts', 3)
        """
        return self.additional_settings.get(key, default)
    
    def set_additional_setting(self, key, value):
        """
        Set a value in additional_settings.
        
        Usage:
            settings.set_additional_setting('email_notifications', True)
            settings.set_additional_setting('company_name', 'Acme Corp')
            settings.save()  # Don't forget to save!
        """
        if self.additional_settings is None:
            self.additional_settings = {}
        self.additional_settings[key] = value
    
    def update_additional_settings(self, settings_dict):
        """
        Update multiple additional settings at once.
        
        Usage:
            settings.update_additional_settings({
                'email_notifications': True,
                'max_login_attempts': 3,
                'company_name': 'Acme Corp'
            })
            settings.save()
        """
        if self.additional_settings is None:
            self.additional_settings = {}
        self.additional_settings.update(settings_dict)
