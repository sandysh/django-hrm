"""
Web views for employee management.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from .models import Employee, Department, Designation
from biometric.tasks import sync_employee_to_device
from zk import ZK, const
from django.conf import settings



def push_user_to_biometric_device(employee, plain_password=None):
    """
    Directly push user to biometric device without Celery.
    Returns: (True, "Success Message") or (False, "Error Message")
    """
    device_ip = settings.BIOMETRIC_DEVICE_IP
    
    # ... (connection logic logic stays same, skipping to keep brevity in tool, I will target the header and body)
    # Actually I will just target the specific lines changed if possible, or rewrite function.
    # It's safer to rewrite the function signature and the set_user call.
    
    device_port = settings.BIOMETRIC_DEVICE_PORT
    password = settings.BIOMETRIC_DEVICE_PASSWORD
    
    conn = None
    
    try:
        # Try TCP first
        try:
            zk = ZK(device_ip, port=device_port, timeout=10, password=password, force_udp=False, ommit_ping=True)
            conn = zk.connect()
        except:
            # Fallback to UDP
            zk = ZK(device_ip, port=device_port, timeout=10, password=password, force_udp=True, ommit_ping=True)
            conn = zk.connect()
            
        if not conn:
            return False, "Could not connect to device (TCP & UDP failed)"
            
        # Determine privilege
        privilege = const.USER_ADMIN if employee.is_staff else const.USER_DEFAULT
        
        # User ID validation (ZK limit)
        uid = employee.id
        if uid > 65535: # Some older devices limit UID
             uid = int(str(uid)[-4:]) 
        
        conn.disable_device()
        
        # Determine password to send
        # If plain_password is provided, use it. Otherwise send empty (or keep existing if update logic supports it?)
        # ZK set_user usually overwrites. If we send empty, it removes password.
        device_password = str(plain_password) if plain_password else ''
        
        conn.set_user(
            uid=uid,
            name=employee.get_full_name()[:24],
            privilege=privilege,
            password=device_password,
            user_id=str(employee.employee_id),
            group_id='',
            card=0
        )
        
        conn.enable_device()
        return True, "User synced to device successfully"
        
    except Exception as e:
        return False, f"Device Error: {str(e)}"
    finally:
        if conn:
            conn.disconnect()


def delete_user_from_device(uid):
    """
    Delete user from biometric device.
    uid: The internal ID (employee.id) used on the device.
    Returns: (True, "Message") or (False, "Error")
    """
    device_ip = settings.BIOMETRIC_DEVICE_IP
    device_port = settings.BIOMETRIC_DEVICE_PORT
    password = settings.BIOMETRIC_DEVICE_PASSWORD
    
    conn = None
    
    try:
        # Try TCP first
        try:
            zk = ZK(device_ip, port=device_port, timeout=10, password=password, force_udp=False, ommit_ping=True)
            conn = zk.connect()
        except:
            # Fallback to UDP
            zk = ZK(device_ip, port=device_port, timeout=10, password=password, force_udp=True, ommit_ping=True)
            conn = zk.connect()
            
        if not conn:
            return False, "Could not connect to device"
        
        # Adjust UID if needed (same logic as push)
        if uid > 65535:
             uid = int(str(uid)[-4:]) 
             
        conn.disable_device()
        conn.delete_user(uid=uid)
        conn.enable_device()
        
        return True, "User deleted from device"
        
    except Exception as e:
        return False, f"Device Error: {str(e)}"
    finally:
        if conn:
            conn.disconnect()


@login_required
def employee_list(request):
    """List all employees (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    employees = Employee.objects.all().order_by('employee_id')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        employees = employees.filter(status=status)
    
    # Search
    search = request.GET.get('search')
    if search:
        employees = employees.filter(
            models.Q(employee_id__icontains=search) |
            models.Q(first_name__icontains=search) |
            models.Q(last_name__icontains=search) |
            models.Q(email__icontains=search)
        )
    
    context = {
        'employees': employees,
        'status_filter': status,
        'search_query': search,
    }
    
    return render(request, 'employees/employee_list.html', context)


def generate_employee_id():
    """
    Generate next employee ID based on last employee.
    Format: EMP0001, EMP0002, etc.
    """
    last_employee = Employee.objects.order_by('-id').first()
    
    if not last_employee or not last_employee.employee_id:
        return 'EMP0001'
    
    # Extract number from last employee ID
    try:
        # Handle formats like EMP0001, EMP001, or just numbers
        last_id = last_employee.employee_id
        # Extract digits from the end
        import re
        match = re.search(r'(\d+)$', last_id)
        if match:
            last_number = int(match.group(1))
            next_number = last_number + 1
            # Maintain same padding as last ID
            padding = len(match.group(1))
            return f'EMP{str(next_number).zfill(padding)}'
        else:
            return 'EMP0001'
    except:
        return 'EMP0001'


@login_required
def employee_create(request):
    """Create new employee (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    designations = Designation.objects.filter(is_active=True).order_by('name')
    
    # Generate next employee ID
    next_employee_id = generate_employee_id()
    
    if request.method == 'POST':
        try:
            # Use provided employee_id or auto-generated one
            employee_id = request.POST.get('employee_id', '').strip() or next_employee_id
            
            employee = Employee.objects.create_user(
                username=request.POST['username'],
                email=request.POST.get('email', ''),
                password=request.POST['password'],
                employee_id=employee_id,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                phone_number=request.POST.get('phone_number', ''),
                department_id=request.POST.get('department') if request.POST.get('department') else None,
                designation_id=request.POST.get('designation') if request.POST.get('designation') else None,
                employment_type=request.POST.get('employment_type', 'FT'),
                status='AC',
                is_staff=request.POST.get('is_staff') == 'on',
            )
            
            # Trigger biometric sync directly (Synchronous)
            # Pass the plain-text password to set it on the device
            plain_password = request.POST.get('password')
            success, msg = push_user_to_biometric_device(employee, plain_password=plain_password)
            
            if success:
                employee.biometric_synced = True
                employee.save()
                messages.success(request, f'Employee created and synced to device! {msg}')
            else:
                messages.warning(request, f'Employee created locally, but device sync failed: {msg}')
            
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error creating employee: {str(e)}')
    
    context = {
        'action': 'Create',
        'departments': departments,
        'designations': designations,
        'next_employee_id': next_employee_id,
    }
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_edit(request, pk):
    """Edit employee (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    employee = get_object_or_404(Employee, pk=pk)
    
    departments = Department.objects.filter(is_active=True).order_by('name')
    designations = Designation.objects.filter(is_active=True).order_by('name')
    
    if request.method == 'POST':
        try:
            employee.employee_id = request.POST.get('employee_id', employee.employee_id)
            employee.first_name = request.POST.get('first_name', '')
            employee.last_name = request.POST.get('last_name', '')
            employee.email = request.POST.get('email', '')
            employee.phone_number = request.POST.get('phone_number', '')
            employee.department_id = request.POST.get('department') if request.POST.get('department') else None
            employee.designation_id = request.POST.get('designation') if request.POST.get('designation') else None
            employee.employment_type = request.POST.get('employment_type', 'FT')
            employee.status = request.POST.get('status', 'AC')
            employee.is_staff = request.POST.get('is_staff') == 'on'
            
            if request.POST.get('password'):
                employee.set_password(request.POST['password'])
            
            employee.save()
            
            # Trigger biometric sync directly (Synchronous)
            plain_password = request.POST.get('password')
            success, msg = push_user_to_biometric_device(employee, plain_password=plain_password)
            
            if success:
                employee.biometric_synced = True
                employee.save()
                messages.success(request, f'Employee updated and synced to device! {msg}')
            else:
                messages.warning(request, f'Employee updated locally, but device sync failed: {msg}')
            
            return redirect('employee_list')
        except Exception as e:
            messages.error(request, f'Error updating employee: {str(e)}')
    
    context = {
        'employee': employee,
        'action': 'Edit',
        'departments': departments,
        'designations': designations,
        'next_employee_id': '',
    }
    
    return render(request, 'employees/employee_form.html', context)


@login_required
def employee_detail(request, pk):
    """View employee details."""
    employee = get_object_or_404(Employee, pk=pk)
    
    # Users can only view their own profile unless they're staff
    if not request.user.is_staff and employee.id != request.user.id:
        messages.error(request, 'You do not have permission to view this page')
        return redirect('dashboard')
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'employees/employee_detail.html', context)


@login_required
def employee_delete(request, pk):
    """Delete employee (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_id = employee.employee_id
        db_id = employee.id
        
        # Try to remove from device
        success, msg = delete_user_from_device(db_id)
        
        # Delete from DB
        employee.delete()
        
        if success:
            messages.success(request, f'Employee {employee_id} deleted successfully from Database and Device!')
        else:
            messages.warning(request, f'Employee {employee_id} deleted from Database, but failed to delete from Device: {msg}')
            
        return redirect('employee_list')
    
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})


@login_required
def employee_sync(request, pk):
    """Manually sync employee to biometric device."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    employee = get_object_or_404(Employee, pk=pk)
    
    success, msg = push_user_to_biometric_device(employee)
    
    if success:
        employee.biometric_synced = True
        employee.save()
        messages.success(request, f'Successfully synced {employee.get_full_name()} to device! {msg}')
    else:
        messages.warning(request, f'Sync failed: {msg}')
        
    return redirect('employee_list')


@login_required
def employee_promote(request, pk):
    """Promote intern to full-time employee (admin only)."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    employee = get_object_or_404(Employee, pk=pk)
    
    # Check if employee is an intern
    if employee.employment_type != 'IN':
        messages.error(request, f'{employee.get_full_name()} is not an intern')
        return redirect('employee_detail', pk=pk)
    
    if request.method == 'POST':
        # Get new employment type from form
        new_employment_type = request.POST.get('employment_type', 'FT')
        
        # Update employee
        employee.employment_type = new_employment_type
        employee.save()
        
        messages.success(
            request, 
            f'{employee.get_full_name()} has been promoted from Intern to {employee.get_employment_type_display()}!'
        )
        return redirect('employee_detail', pk=pk)
    
    context = {
        'employee': employee,
    }
    
    return render(request, 'employees/employee_promote.html', context)

