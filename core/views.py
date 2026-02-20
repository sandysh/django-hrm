"""
Views for the main dashboard and authentication.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from employees.models import Employee
from attendance.models import AttendanceRecord, DailyAttendance
from leaves.models import LeaveRequest, LeaveBalance, LeaveType


def login_view(request):
    """Login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'core/login.html')


def logout_view(request):
    """Logout user."""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('login')


@login_required
def dashboard(request):
    """Main dashboard - redirects based on user role."""
    if request.user.is_staff:
        return admin_dashboard(request)
    else:
        return user_dashboard(request)


@login_required
def admin_dashboard(request):
    """Admin dashboard with statistics."""
    # Employee statistics
    total_employees = Employee.objects.filter(status='AC').count()
    synced_employees = Employee.objects.filter(biometric_synced=True).count()
    
    # Today's attendance
    today = timezone.now().date()
    present_today = DailyAttendance.objects.filter(
        date=today,
        status__in=['PR', 'LT']
    ).count()
    
    absent_today = total_employees - present_today
    
    # Leave requests
    pending_leaves = LeaveRequest.objects.filter(status='PE').count()
    
    # Recent attendance
    recent_attendance = DailyAttendance.objects.select_related('employee').filter(
        date=today
    ).order_by('-check_in_time')[:10]
    
    # Pending leave requests
    pending_leave_requests = LeaveRequest.objects.select_related(
        'employee', 'leave_type'
    ).filter(status='PE').order_by('-created_at')[:5]
    
    # Department-wise attendance
    dept_attendance = DailyAttendance.objects.filter(
        date=today
    ).values('employee__department').annotate(
        present=Count('id', filter=Q(status__in=['PR', 'LT']))
    )
    
    context = {
        'total_employees': total_employees,
        'synced_employees': synced_employees,
        'present_today': present_today,
        'absent_today': absent_today,
        'pending_leaves': pending_leaves,
        'recent_attendance': recent_attendance,
        'pending_leave_requests': pending_leave_requests,
        'dept_attendance': dept_attendance,
    }
    
    return render(request, 'core/admin_dashboard.html', context)


@login_required
def user_dashboard(request):
    """User dashboard with personal stats."""
    employee = request.user
    today = timezone.now().date()
    current_month = today.replace(day=1)
    
    # Today's attendance
    today_attendance = DailyAttendance.objects.filter(
        employee=employee,
        date=today
    ).first()
    
    # Check if already punched in today
    last_punch = AttendanceRecord.objects.filter(
        employee=employee,
        punch_time__date=today
    ).order_by('-punch_time').first()
    
    # This month's stats
    month_attendance = DailyAttendance.objects.filter(
        employee=employee,
        date__gte=current_month,
        date__lte=today
    )
    
    present_days = month_attendance.filter(status__in=['PR', 'LT']).count()
    total_hours = month_attendance.aggregate(Sum('total_hours'))['total_hours__sum'] or 0
    late_days = month_attendance.filter(is_late=True).count()
    
    # Leave balance
    current_year = today.year
    leave_balances = LeaveBalance.objects.filter(
        employee=employee,
        year=current_year
    ).select_related('leave_type')
    
    # Recent leave requests
    recent_leaves = LeaveRequest.objects.filter(
        employee=employee
    ).select_related('leave_type').order_by('-created_at')[:5]
    
    # Recent attendance
    recent_attendance = DailyAttendance.objects.filter(
        employee=employee
    ).order_by('-date')[:7]
    
    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'last_punch': last_punch,
        'present_days': present_days,
        'total_hours': round(total_hours, 2),
        'late_days': late_days,
        'leave_balances': leave_balances,
        'recent_leaves': recent_leaves,
        'recent_attendance': recent_attendance,
    }
    
    return render(request, 'core/user_dashboard.html', context)
