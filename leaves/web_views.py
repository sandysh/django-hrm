"""
Web views for leave management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from leaves.models import LeaveRequest, LeaveType, Holiday


@login_required
def leave_apply(request):
    """Apply for leave."""
    leave_types = LeaveType.objects.filter(is_active=True)
    current_year = timezone.now().year
    
    # Calculate remaining days for each leave type
    leave_type_data = []
    for leave_type in leave_types:
        # Get total approved days for this leave type in current year
        approved_leaves = LeaveRequest.objects.filter(
            employee=request.user,
            leave_type=leave_type,
            status='AP',
            start_date__year=current_year
        )
        
        total_used = sum(leave.total_days for leave in approved_leaves)
        remaining = leave_type.default_days - total_used
        
        leave_type_data.append({
            'leave_type': leave_type,
            'total_days': leave_type.default_days,
            'used_days': total_used,
            'remaining_days': remaining
        })
    
    if request.method == 'POST':
        try:
            leave_type = LeaveType.objects.get(id=request.POST['leave_type'])
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()
            
            # Validate dates
            if end_date < start_date:
                messages.error(request, 'End date must be after start date')
                return redirect('leave_apply')
            
            # Calculate days
            total_days = (end_date - start_date).days + 1
            
            # Create leave request
            LeaveRequest.objects.create(
                employee=request.user,
                leave_type=leave_type,
                start_date=start_date,
                end_date=end_date,
                total_days=total_days,
                reason=request.POST.get('reason', ''),
                status='PE'
            )
            
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('my_leaves')
        except Exception as e:
            messages.error(request, f'Error submitting leave request: {str(e)}')
    
    context = {
        'leave_types': leave_types,
        'leave_type_data': leave_type_data,
    }
    
    return render(request, 'leaves/leave_form.html', context)


@login_required
def my_leaves(request):
    """View own leave requests."""
    leave_requests = LeaveRequest.objects.filter(
        employee=request.user
    ).select_related('leave_type', 'approved_by').order_by('-created_at')
    
    context = {
        'leave_requests': leave_requests,
    }
    
    return render(request, 'leaves/my_leaves.html', context)


@login_required
def leave_requests(request):
    """View all leave requests (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    # Filter by status
    status = request.GET.get('status', 'PE')
    leave_requests = LeaveRequest.objects.select_related(
        'employee', 'leave_type', 'approved_by'
    ).order_by('-created_at')
    
    if status:
        leave_requests = leave_requests.filter(status=status)
    
    context = {
        'leave_requests': leave_requests,
        'status_filter': status,
    }
    
    return render(request, 'leaves/leave_list.html', context)


@login_required
def leave_detail(request, pk):
    """View leave request details."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    # Users can only view their own leaves unless they're staff
    if not request.user.is_staff and leave_request.employee.id != request.user.id:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    context = {
        'leave_request': leave_request,
    }
    
    return render(request, 'leaves/leave_detail.html', context)


@login_required
def leave_edit(request, pk):
    """Edit a pending leave request. Employees can edit their own; admin can edit any."""
    leave_request = get_object_or_404(LeaveRequest, pk=pk)

    # Permission: must be own leave or staff
    if not request.user.is_staff and leave_request.employee.id != request.user.id:
        messages.error(request, 'You do not have permission to edit this leave')
        return redirect('dashboard')

    # Only pending leaves can be edited
    if leave_request.status != 'PE':
        messages.error(request, 'Only pending leave requests can be edited')
        if request.user.is_staff:
            return redirect('leave_requests')
        return redirect('my_leaves')

    leave_types = LeaveType.objects.filter(is_active=True)

    if request.method == 'POST':
        try:
            leave_type = LeaveType.objects.get(id=request.POST['leave_type'])
            start_date = datetime.strptime(request.POST['start_date'], '%Y-%m-%d').date()
            end_date = datetime.strptime(request.POST['end_date'], '%Y-%m-%d').date()

            if end_date < start_date:
                messages.error(request, 'End date must be after start date')
                return redirect('leave_edit', pk=pk)

            leave_request.leave_type = leave_type
            leave_request.start_date = start_date
            leave_request.end_date = end_date
            leave_request.reason = request.POST.get('reason', '')
            leave_request.save()

            messages.success(request, 'Leave request updated successfully!')
            if request.user.is_staff:
                return redirect('leave_requests')
            return redirect('my_leaves')
        except Exception as e:
            messages.error(request, f'Error updating leave request: {str(e)}')

    context = {
        'leave_request': leave_request,
        'leave_types': leave_types,
        'is_edit': True,
    }
    return render(request, 'leaves/leave_form.html', context)


@login_required
def leave_approve(request, pk):
    """Approve leave request (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if leave_request.status != 'PE':
        messages.error(request, 'Only pending requests can be approved')
        return redirect('leave_requests')
    
    leave_request.status = 'AP'
    leave_request.approved_by = request.user
    leave_request.approved_at = timezone.now()
    leave_request.approval_notes = request.POST.get('notes', '')
    leave_request.save()
    
    messages.success(request, 'Leave request approved successfully!')
    return redirect('leave_requests')


@login_required
def leave_reject(request, pk):
    """Reject leave request (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if leave_request.status != 'PE':
        messages.error(request, 'Only pending requests can be rejected')
        return redirect('leave_requests')
    
    leave_request.status = 'RJ'
    leave_request.approved_by = request.user
    leave_request.approved_at = timezone.now()
    leave_request.approval_notes = request.POST.get('notes', '')
    leave_request.save()
    
    messages.success(request, 'Leave request rejected!')
    return redirect('leave_requests')


@login_required
def holiday_calendar(request):
    """Render the holiday calendar view."""
    if not request.user.is_staff:
         messages.error(request, 'You do not have permission to view this page')
         return redirect('dashboard')
    return render(request, 'leaves/holidays.html')


@login_required
def holiday_api(request):
    """API for managing holidays."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    if request.method == 'GET':
        holidays = Holiday.objects.all()
        events = []
        for h in holidays:
            events.append({
                'id': h.id,
                'title': f"{h.name}",
                'start': h.date.isoformat(),
                'allDay': True,
                'backgroundColor': '#EF4444', # Red
                'borderColor': '#EF4444',
                'extendedProps': {
                    'description': h.description
                }
            })
        return JsonResponse(events, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            date = data.get('date')
            name = data.get('name')
            
            if not date or not name:
                return JsonResponse({'error': 'Date and name required'}, status=400)
            
            # Check for existing
            if Holiday.objects.filter(date=date).exists():
                return JsonResponse({'error': 'Holiday already exists for this date'}, status=400)

            holiday = Holiday.objects.create(date=date, name=name, is_optional=False)
            return JsonResponse({'id': holiday.id, 'message': 'Holiday created'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@require_http_methods(["DELETE"])
def holiday_delete(request, pk):
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        holiday = Holiday.objects.get(pk=pk)
        holiday.delete()
        return JsonResponse({'message': 'Deleted'})
    except Holiday.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

@login_required
def user_calendar(request):
    """Render the user calendar view."""
    return render(request, 'leaves/user_calendar.html')

@login_required
def user_calendar_api(request):
    """API for user calendar events (Holidays + My Approved Leaves)."""
    events = []
    
    # 1. Holidays
    holidays = Holiday.objects.all()
    for h in holidays:
        # Event bubble
        events.append({
             'title': f"🌴 {h.name}",
             'start': h.date.isoformat(),
             'allDay': True,
             'backgroundColor': '#EF4444', # Red
             'borderColor': '#EF4444',
             'extendedProps': {'type': 'holiday'}
        })

    # 2. My Approved Leaves
    leaves = LeaveRequest.objects.filter(employee=request.user, status='AP')
    for l in leaves:
        title = f"🏖️ On Leave: {l.leave_type.name}"
        # FullCalendar end date is exclusive, so add 1 day
        end_date = l.end_date + timedelta(days=1)
        
        events.append({
            'title': title,
            'start': l.start_date.isoformat(),
            'end': end_date.isoformat(),
            'allDay': True,
            'backgroundColor': '#3B82F6', # Blue
            'borderColor': '#3B82F6',
            'extendedProps': {'type': 'leave'}
        })

    return JsonResponse(events, safe=False)
