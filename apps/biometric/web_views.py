"""
Web views for biometric device management.
"""
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from zk import ZK


@login_required
def test_device_connection(request):
    """Test connection to the biometric device."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')
    
    device_ip = settings.BIOMETRIC_DEVICE_IP
    device_port = settings.BIOMETRIC_DEVICE_PORT
    
    conn = None
    try:
        # Try 1: TCP Connection (force_udp=False)
        try:
            zk = ZK(
                device_ip, 
                port=device_port, 
                timeout=15, 
                password=settings.BIOMETRIC_DEVICE_PASSWORD, 
                force_udp=False, 
                ommit_ping=True
            )
            conn = zk.connect()
            mode = "TCP"
        except Exception:
            # Try 2: UDP Connection (force_udp=True)
            zk = ZK(
                device_ip, 
                port=device_port, 
                timeout=15, 
                password=settings.BIOMETRIC_DEVICE_PASSWORD, 
                force_udp=True, 
                ommit_ping=True
            )
            conn = zk.connect()
            mode = "UDP"

        # If we reach here, one of them succeeded
        firmware = conn.get_firmware_version()
        serial = conn.get_serialnumber()
        
        messages.success(
            request, 
            f'✅ Connection Successful using {mode}! Device: {device_ip}:{device_port} '
            f'(Firmware: {firmware}, Serial: {serial})'
        )
        
    except Exception as e:
        messages.error(
            request, 
            f'❌ Connection Failed (Tried TCP & UDP): {str(e)}. Check IP {device_ip} and cable.'
        )
    finally:
        if conn:
            conn.disconnect()
            
    return redirect('dashboard')


@login_required
def sync_attendance_data(request):
    """Manually pull attendance logs from the device with range filtering."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to perform this action')
        return redirect('dashboard')

    # Imports locally
    from employees.models import Employee
    from attendance.models import AttendanceRecord
    from biometric.tasks import update_daily_attendance
    from django.utils import timezone
    from datetime import timedelta
    import calendar
    
    # Determine Date Range
    range_type = request.GET.get('range', 'today')
    now = timezone.now()
    today = now.date()
    
    start_date = None
    end_date = None
    
    if range_type == 'today':
        start_date = today
        end_date = today
    elif range_type == 'yesterday':
        start_date = today - timedelta(days=1)
        end_date = start_date
    elif range_type == 'this_week':
        # Start of week (assuming Monday is 0)
        start_date = today - timedelta(days=today.weekday())
        end_date = today
    elif range_type == 'last_week':
        start_of_this_week = today - timedelta(days=today.weekday())
        start_date = start_of_this_week - timedelta(days=7)
        end_date = start_of_this_week - timedelta(days=1)
    elif range_type == 'last_month':
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        start_date = last_month_end.replace(day=1)
        end_date = last_month_end
    elif range_type == 'all':
        start_date = None
        end_date = None
    else:
        # Default to today if unknown
        start_date = today
        end_date = today

    device_ip = settings.BIOMETRIC_DEVICE_IP
    device_port = settings.BIOMETRIC_DEVICE_PORT
    password = settings.BIOMETRIC_DEVICE_PASSWORD
    
    conn = None
    records_added = 0
    records_processed_count = 0
    records_total = 0
    
    try:
        # Establish Connection
        try:
            zk = ZK(device_ip, port=device_port, timeout=20, password=password, force_udp=False, ommit_ping=True)
            conn = zk.connect()
        except:
            zk = ZK(device_ip, port=device_port, timeout=20, password=password, force_udp=True, ommit_ping=True)
            conn = zk.connect()
            
        if not conn:
            messages.error(request, "Could not connect to device (TCP & UDP failed).")
            return redirect('dashboard')
            
        conn.disable_device()
        attendances = conn.get_attendance()
        conn.enable_device()
        
        records_total = len(attendances)
        
        # Determine employee map for speed
        # Map user_id (str) -> Employee
        # Map biometric_id (int) -> Employee
        # For now, keep simple loop lookup or optimize if needed. 
        # With SQL overhead, simple lookups are fine for <1000 records.
        
        for att in attendances:
            try:
                # Filter by Date
                att_time = timezone.make_aware(att.timestamp)
                att_date = att_time.date()
                
                if start_date and att_date < start_date:
                    continue
                if end_date and att_date > end_date:
                    continue
                
                records_processed_count += 1

                # Find Employee
                employee = Employee.objects.filter(employee_id=att.user_id).first()
                if not employee and att.user_id.isdigit():
                     employee = Employee.objects.filter(biometric_user_id=int(att.user_id)).first()
                     
                if employee:
                    record, created = AttendanceRecord.objects.get_or_create(
                        employee=employee,
                        punch_time=att_time,
                        defaults={
                            'punch_type': 'IN',
                            'biometric_user_id': int(att.uid) if hasattr(att, 'uid') else None,
                            'punch_state': att.punch,
                            'verify_type': att.status
                        }
                    )
                    
                    if created:
                        records_added += 1
                        update_daily_attendance(employee, att_date)
            except Exception:
                pass 
                
        range_label = range_type.replace('_', ' ').title()
        messages.success(request, f"Synced {range_label}: Processed {records_processed_count}/{records_total} logs. Added {records_added} new.")
        
    except Exception as e:
        messages.error(request, f"Sync Error: {str(e)}")
    finally:
        if conn:
            conn.disconnect()
            
    return redirect('dashboard')
