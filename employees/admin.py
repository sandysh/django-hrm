"""
Admin configuration for Employee model.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Employee, Department, Designation


@admin.register(Employee)
class EmployeeAdmin(UserAdmin):
    """
    Admin interface for Employee model.
    """
    list_display = ['employee_id', 'username', 'get_full_name', 'email', 'department', 
                   'designation', 'employment_type', 'status', 'biometric_synced']
    list_filter = ['status', 'employment_type', 'department', 'biometric_synced', 'gender']
    search_fields = ['employee_id', 'username', 'first_name', 'last_name', 'email']
    readonly_fields = ['created_at', 'updated_at', 'biometric_sync_date']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Information', {
            'fields': ('employee_id', 'phone_number', 'date_of_birth', 'gender', 
                      'address', 'profile_picture')
        }),
        ('Employment Information', {
            'fields': ('department', 'designation', 'employment_type', 
                      'date_joined_company', 'status')
        }),
        ('Biometric Information', {
            'fields': ('biometric_user_id', 'biometric_synced', 'biometric_sync_date')
        }),
        ('Leave Balance', {
            'fields': ('annual_leave_balance', 'sick_leave_balance', 'casual_leave_balance')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Information', {
            'fields': ('employee_id', 'first_name', 'last_name', 'email', 
                      'phone_number', 'department', 'designation')
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


@admin.register(Designation)
class DesignationAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'is_active', 'created_at']
    list_filter = ['is_active', 'department', 'created_at']
    search_fields = ['name', 'code', 'description']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'department', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

