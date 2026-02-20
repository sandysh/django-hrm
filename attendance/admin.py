from django.contrib import admin
from .models import AttendanceRecord, DailyAttendance


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
