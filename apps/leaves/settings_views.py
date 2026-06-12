"""
Views for leave settings management (superadmin only).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LeaveType


@login_required
def leave_settings(request):
    """Display leave types settings page."""
    if not request.user.is_superuser:
        messages.error(request, 'Only superadmin can access settings')
        return redirect('dashboard')
    
    from core.models import SystemSettings
    
    leave_types = LeaveType.objects.all().order_by('name')
    system_settings = SystemSettings.get_settings()
    
    # Handle system settings update
    if request.method == 'POST' and 'update_office_hours' in request.POST:
        try:
            system_settings.office_start_time = request.POST.get('office_start_time')
            system_settings.office_end_time = request.POST.get('office_end_time')
            system_settings.late_threshold_minutes = int(request.POST.get('late_threshold_minutes', 15))
            system_settings.save()
            
            messages.success(request, 'Office hours updated successfully!')
            return redirect('settings')
        except Exception as e:
            messages.error(request, f'Error updating office hours: {str(e)}')
    
    context = {
        'leave_types': leave_types,
        'system_settings': system_settings,
    }
    
    return render(request, 'leaves/settings.html', context)


@login_required
def leave_type_create(request):
    """Create a new leave type."""
    if not request.user.is_superuser:
        messages.error(request, 'Only superadmin can create leave types')
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            leave_type = LeaveType.objects.create(
                name=request.POST['name'],
                code=request.POST['code'].upper(),
                description=request.POST.get('description', ''),
                default_days=int(request.POST.get('default_days', 0)),
                is_paid=request.POST.get('is_paid') == 'on',
                requires_approval=request.POST.get('requires_approval', 'on') == 'on',
                is_active=True
            )
            messages.success(request, f'Leave type "{leave_type.name}" created successfully!')
            return redirect('settings')
        except Exception as e:
            messages.error(request, f'Error creating leave type: {str(e)}')
    
    return render(request, 'leaves/leave_type_form.html', {'action': 'Create'})


@login_required
def leave_type_edit(request, pk):
    """Edit an existing leave type."""
    if not request.user.is_superuser:
        messages.error(request, 'Only superadmin can edit leave types')
        return redirect('dashboard')
    
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    if request.method == 'POST':
        try:
            leave_type.name = request.POST['name']
            leave_type.code = request.POST['code'].upper()
            leave_type.description = request.POST.get('description', '')
            leave_type.default_days = int(request.POST.get('default_days', 0))
            leave_type.is_paid = request.POST.get('is_paid') == 'on'
            leave_type.requires_approval = request.POST.get('requires_approval', 'on') == 'on'
            leave_type.is_active = request.POST.get('is_active') == 'on'
            leave_type.save()
            
            messages.success(request, f'Leave type "{leave_type.name}" updated successfully!')
            return redirect('settings')
        except Exception as e:
            messages.error(request, f'Error updating leave type: {str(e)}')
    
    context = {
        'leave_type': leave_type,
        'action': 'Edit'
    }
    
    return render(request, 'leaves/leave_type_form.html', context)


@login_required
def leave_type_delete(request, pk):
    """Delete a leave type."""
    if not request.user.is_superuser:
        messages.error(request, 'Only superadmin can delete leave types')
        return redirect('dashboard')
    
    leave_type = get_object_or_404(LeaveType, pk=pk)
    
    if request.method == 'POST':
        name = leave_type.name
        try:
            leave_type.delete()
            messages.success(request, f'Leave type "{name}" deleted successfully!')
        except Exception as e:
            messages.error(request, f'Error deleting leave type: {str(e)}')
        return redirect('settings')
    
    context = {
        'leave_type': leave_type,
    }
    
    return render(request, 'leaves/leave_type_confirm_delete.html', context)
