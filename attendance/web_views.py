"""
Web views for attendance management.
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from attendance.models import AttendanceRecord, DailyAttendance
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

    from employees.models import Employee

    today = timezone.now().date()
    
    # Parse date range (defaults will be adjusted on the client to be Nepali month-based)
    start_date_param = request.GET.get('start_date')
    end_date_param = request.GET.get('end_date')
    is_default_start = not start_date_param
    is_default_end = not end_date_param

    # Month boundaries (computed on client from Nepali/Bikram Sambat) used for
    # "Remaining Hours" card calculations. Expected to be AD YYYY-MM-DD.
    month_start_param = request.GET.get('month_start_date')
    month_end_param = request.GET.get('month_end_date')

    first_of_month = today.replace(day=1)
    
    try:
        start_date = datetime.strptime(start_date_param, '%Y-%m-%d').date() if start_date_param else first_of_month
    except ValueError:
        start_date = first_of_month
    
    try:
        end_date = datetime.strptime(end_date_param, '%Y-%m-%d').date() if end_date_param else today
    except ValueError:
        end_date = today

    # Defaults: use the selected range itself.
    try:
        month_start_date = datetime.strptime(month_start_param, '%Y-%m-%d').date() if month_start_param else start_date
    except ValueError:
        month_start_date = start_date

    try:
        month_end_date = datetime.strptime(month_end_param, '%Y-%m-%d').date() if month_end_param else end_date
    except ValueError:
        month_end_date = end_date

    if month_start_date > month_end_date:
        month_start_date, month_end_date = month_end_date, month_start_date

    worked_end_date = min(end_date, month_end_date)

    # Clamp so start <= end
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    # Optional employee filter
    employee_id_param = request.GET.get('employee_id')
    selected_employee = None
    if employee_id_param:
        try:
            selected_employee = Employee.objects.get(pk=employee_id_param)
        except Employee.DoesNotExist:
            selected_employee = None

    # All active employees for the dropdown
    all_employees = Employee.objects.filter(
        is_active=True, is_staff=False
    ).order_by('employee_id')

    # Build queryset
    attendance_records = DailyAttendance.objects.filter(
        date__gte=start_date,
        date__lte=end_date,
    ).select_related('employee').order_by('employee__employee_id', 'date')

    if selected_employee:
        attendance_records = attendance_records.filter(employee=selected_employee).order_by('date')

    # Statistics
    total_records = attendance_records.count()
    present = attendance_records.filter(status__in=['PR', 'LT']).count()
    absent = attendance_records.filter(status='AB').count()
    on_leave = attendance_records.filter(status='LV').count()
    late = attendance_records.filter(is_late=True).count()
    total_hours = sum(r.total_hours or 0 for r in attendance_records)

    # Expected hours (worked out of X) and per-day diff using same logic as user dashboard
    expected_hours = 0.0
    standard_hours = 0.0
    try:
        from core.models import SystemSettings
        from leaves.models import Holiday
        from datetime import datetime as dt

        settings = SystemSettings.get_settings()
        standard_hours = float(settings.standard_work_hours)

        # Hours per working day from office timings
        start_dt = dt.combine(start_date, settings.office_start_time)
        end_dt = dt.combine(start_date, settings.office_end_time)
        hours_per_day = (end_dt - start_dt).total_seconds() / 3600.0

        # Holidays in the selected range
        holidays = set(
            Holiday.objects.filter(
                date__gte=start_date,
                date__lte=end_date,
            ).values_list('date', flat=True)
        )

        current = start_date
        while current <= end_date:
            # Skip Saturday (weekday 5) and holidays, same as employee dashboard logic
            if current.weekday() != 5 and current not in holidays:
                expected_hours += hours_per_day
            current += timedelta(days=1)

        # Attach per-record diff vs standard hours (missed / extra)
        if standard_hours > 0:
            for rec in attendance_records:
                hours = float(rec.total_hours or 0)
                diff = standard_hours - hours
                rec.missed_hours = round(diff, 2) if diff > 0 else 0
                rec.extra_hours = round(-diff, 2) if diff < 0 else 0
    except Exception:
        expected_hours = 0.0
        standard_hours = 0.0

    # Monthly remaining hours for selected employee (same logic as user dashboard)
    monthly_expected_hours = 0.0
    monthly_remaining_hours = 0.0
    if selected_employee:
        try:
            from core.models import SystemSettings
            from leaves.models import Holiday
            from datetime import datetime as dt

            # Nepali (BS) month range (computed on client, AD values)
            # - month_start_date: BS month day 1 (AD)
            # - month_end_date: BS month end (AD)
            # - worked_end_date: up to selected end_date (usually today)
            month_attendance = DailyAttendance.objects.filter(
                employee=selected_employee,
                date__gte=month_start_date,
                date__lte=worked_end_date,
            )
            month_total_hours = sum(a.total_hours or 0 for a in month_attendance)

            settings = SystemSettings.get_settings()

            # Hours per working day using office timings
            start_dt = dt.combine(month_start_date, settings.office_start_time)
            end_dt = dt.combine(month_start_date, settings.office_end_time)
            hours_per_day = (end_dt - start_dt).total_seconds() / 3600.0

            holidays_this_month = set(
                Holiday.objects.filter(
                    date__gte=month_start_date,
                    date__lte=month_end_date,
                ).values_list('date', flat=True)
            )

            expected = 0.0
            current = month_start_date
            while current <= month_end_date:
                # Saturday is weekday 5 (0=Monday, 6=Sunday). We skip Saturday and any Holiday.
                if current.weekday() != 5 and current not in holidays_this_month:
                    expected += hours_per_day
                current += timedelta(days=1)

            monthly_expected_hours = expected
            monthly_remaining_hours = max(0.0, expected - float(month_total_hours))
        except Exception:
            monthly_expected_hours = 0.0
            monthly_remaining_hours = 0.0

    context = {
        'attendance_records': attendance_records,
        'start_date': start_date,
        'end_date': end_date,
        'is_default_start': is_default_start,
        'is_default_end': is_default_end,
        'all_employees': all_employees,
        'selected_employee': selected_employee,
        'selected_employee_id': employee_id_param or '',
        'total_records': total_records,
        'present': present,
        'absent': absent,
        'on_leave': on_leave,
        'late': late,
        'total_hours': round(total_hours, 2),
        'expected_hours': round(expected_hours, 2) if expected_hours else 0,
        'standard_hours': round(standard_hours, 2) if standard_hours else 0,
        'monthly_expected_hours': round(monthly_expected_hours, 2) if monthly_expected_hours else 0,
        'monthly_remaining_hours': round(monthly_remaining_hours, 2) if monthly_remaining_hours else 0,
    }

    return render(request, 'attendance/report.html', context)
