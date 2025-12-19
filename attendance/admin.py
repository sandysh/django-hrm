from django.contrib import admin
from .models import AttendanceRecord, DailyAttendance, AttendanceSettings


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'punch_time', 'punch_type', 'biometric_user_id', 'is_manual', 'synced_at']
    list_filter = ['punch_type', 'is_manual', 'punch_time']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['synced_at']
    date_hierarchy = 'punch_time'
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('employee', 'punch_time', 'punch_type')
        }),
        ('Biometric Data', {
            'fields': ('biometric_user_id', 'device_id', 'punch_state', 'verify_type')
        }),
        ('Additional Information', {
            'fields': ('is_manual', 'notes', 'synced_at')
        }),
    )


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'status', 'check_in_time', 'check_out_time', 
                   'total_hours', 'is_late', 'is_overtime']
    list_filter = ['status', 'is_late', 'is_overtime', 'date']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('employee', 'date', 'status')
        }),
        ('Time Tracking', {
            'fields': ('check_in_time', 'check_out_time', 'total_hours', 'total_break_time')
        }),
        ('Flags', {
            'fields': ('is_late', 'is_early_departure', 'is_overtime', 'overtime_hours')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


@admin.register(AttendanceSettings)
class AttendanceSettingsAdmin(admin.ModelAdmin):
    list_display = ['standard_work_hours', 'shift_start_time', 'shift_end_time', 
                   'grace_period_minutes', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Working Hours', {
            'fields': ('standard_work_hours', 'shift_start_time', 'shift_end_time')
        }),
        ('Policies', {
            'fields': ('grace_period_minutes', 'lunch_break_duration', 
                      'overtime_threshold_hours', 'half_day_threshold_hours')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        # Only allow one settings instance
        return not AttendanceSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Don't allow deletion of settings
        return False
