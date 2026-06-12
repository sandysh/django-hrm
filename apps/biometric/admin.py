from django.contrib import admin
from .models import BiometricDevice, SyncLog


@admin.register(BiometricDevice)
class BiometricDeviceAdmin(admin.ModelAdmin):
    list_display = ['name', 'ip_address', 'port', 'is_active', 'last_connection_status', 
                   'last_sync_time', 'firmware_version']
    list_filter = ['is_active', 'last_connection_status']
    search_fields = ['name', 'ip_address', 'serial_number']
    readonly_fields = ['serial_number', 'firmware_version', 'platform', 'device_name',
                      'last_sync_time', 'last_connection_status', 'last_error', 
                      'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'ip_address', 'port', 'password', 'timeout', 'is_active')
        }),
        ('Device Information', {
            'fields': ('serial_number', 'firmware_version', 'platform', 'device_name')
        }),
        ('Status', {
            'fields': ('last_connection_status', 'last_sync_time', 'last_error')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(SyncLog)
class SyncLogAdmin(admin.ModelAdmin):
    list_display = ['sync_type', 'status', 'records_processed', 'records_success', 
                   'records_failed', 'started_at', 'duration_seconds']
    list_filter = ['sync_type', 'status', 'started_at']
    search_fields = ['error_message']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Sync Information', {
            'fields': ('device', 'sync_type', 'status')
        }),
        ('Statistics', {
            'fields': ('records_processed', 'records_success', 'records_failed')
        }),
        ('Timing', {
            'fields': ('started_at', 'completed_at', 'duration_seconds')
        }),
        ('Details', {
            'fields': ('error_message', 'details')
        }),
    )
    
    def has_add_permission(self, request):
        # Sync logs are created automatically
        return False
    
    def has_change_permission(self, request, obj=None):
        # Sync logs should not be edited
        return False
