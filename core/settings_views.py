"""
Views for system settings management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import SystemSettings


@login_required
def settings(request):
    """Unified settings page for all system configurations (superadmin only)."""
    if not request.user.is_superuser:
        messages.error(request, 'Only superadmin can access settings')
        return redirect('dashboard')
    
    from leaves.models import LeaveType
    
    system_settings = SystemSettings.get_settings()
    leave_types = LeaveType.objects.all().order_by('name')
    
    # Handle office hours update
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
        'system_settings': system_settings,
        'leave_types': leave_types,
    }
    
    return render(request, 'core/settings.html', context)
