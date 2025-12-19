"""
Web views for attendance management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from attendance.models import AttendanceRecord, DailyAttendance, AttendanceSettings
from biometric.tasks import update_daily_attendance


@login_required
def punch_attendance(request):
    """Web-based punch in/out."""
    employee = request.user
    today = timezone.now().date()
    now = timezone.now()
    
    # Get today's attendance record
    today_attendance = DailyAttendance.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    # Get last punch record
    last_punch = AttendanceRecord.objects.filter(
        employee=employee,
        punch_time__date=today
    ).order_by('-punch_time').first()
    
    # Determine next punch type
    if not last_punch or last_punch.punch_type in ['OUT', 'BREAK_IN']:
        next_punch_type = 'IN'
        next_punch_label = 'Punch In'
        next_punch_color = 'success'
    else:
        next_punch_type = 'OUT'
        next_punch_label = 'Punch Out'
        next_punch_color = 'danger'
    
    if request.method == 'POST':
        punch_type = request.POST.get('punch_type', next_punch_type)
        
        # Create attendance record
        AttendanceRecord.objects.create(
            employee=employee,
            punch_time=now,
            punch_type=punch_type,
            biometric_user_id=employee.biometric_user_id or 0,
            is_manual=True,
            notes='Web punch'
        )
        
        # Update daily attendance
        update_daily_attendance(employee, today)
        
        messages.success(request, f'Successfully punched {punch_type.lower()}!')
        return redirect('punch_attendance')
    
    # Get all punches for today
    today_punches = AttendanceRecord.objects.filter(
        employee=employee,
        punch_time__date=today
    ).order_by('punch_time')
    
    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'last_punch': last_punch,
        'today_punches': today_punches,
        'next_punch_type': next_punch_type,
        'next_punch_label': next_punch_label,
        'next_punch_color': next_punch_color,
        'current_time': now,
    }
    
    return render(request, 'attendance/punch.html', context)


@login_required
def my_attendance(request):
    """View own attendance history."""
    employee = request.user
    
    # Get date range from query params
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Default to current month
    if not start_date:
        start_date = timezone.now().date().replace(day=1)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    
    if not end_date:
        end_date = timezone.now().date()
    else:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Get attendance records
    attendance_records = DailyAttendance.objects.filter(
        employee=employee,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('-date')
    
    # Calculate statistics
    total_days = attendance_records.count()
    present_days = attendance_records.filter(status__in=['PR', 'LT']).count()
    absent_days = attendance_records.filter(status='AB').count()
    late_days = attendance_records.filter(is_late=True).count()
    total_hours = sum([a.total_hours or 0 for a in attendance_records])
    
    context = {
        'attendance_records': attendance_records,
        'start_date': start_date,
        'end_date': end_date,
        'total_days': total_days,
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'total_hours': round(total_hours, 2),
    }
    
    return render(request, 'attendance/my_attendance.html', context)


@login_required
def attendance_report(request):
    """Admin view for attendance reports."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    today = timezone.now().date()
    
    # Get date from query params or use today
    date_param = request.GET.get('date')
    if date_param:
        try:
            date = datetime.strptime(date_param, '%Y-%m-%d').date()
        except ValueError:
            date = today
    else:
        date = today
    
    # Get all attendance for the date
    attendance_records = DailyAttendance.objects.filter(
        date=date
    ).select_related('employee').order_by('employee__employee_id')
    
    # Calculate statistics
    total_employees = attendance_records.count()
    present = attendance_records.filter(status__in=['PR', 'LT']).count()
    absent = attendance_records.filter(status='AB').count()
    on_leave = attendance_records.filter(status='LV').count()
    late = attendance_records.filter(is_late=True).count()
    
    context = {
        'attendance_records': attendance_records,
        'date': date,
        'total_employees': total_employees,
        'present': present,
        'absent': absent,
        'on_leave': on_leave,
        'late': late,
    }
    
    return render(request, 'attendance/report.html', context)
