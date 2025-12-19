"""
Admin configuration for Department and Designation models.
"""
from django.contrib import admin
from .department_models import Department, Designation


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
