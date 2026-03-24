"""
Celery tasks for biometric device synchronization.
"""
import logging
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
from .services import BiometricDeviceService
from .models import BiometricDevice, SyncLog
from employees.models import Employee
from attendance.models import AttendanceRecord, DailyAttendance

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def sync_employee_to_device(self, employee_id: int):
    """
    Sync a single employee to the biometric device.
    """
    sync_log = SyncLog.objects.create(
        sync_type='USER_PUSH',
        status='FA',  # Will update to SU if successful
        records_processed=1
    )
    
    try:
        employee = Employee.objects.get(id=employee_id)
        
        # Get or create biometric UID
        if not employee.biometric_user_id:
            # Find next available UID
            max_uid = Employee.objects.filter(
                biometric_user_id__isnull=False
            ).order_by('-biometric_user_id').first()
            
            employee.biometric_user_id = (max_uid.biometric_user_id + 1) if max_uid else 1
            employee.save()
        
        # Connect to device and create/update user
        with BiometricDeviceService() as device_service:
            device_service.create_user(
                uid=employee.biometric_user_id,
                name=employee.get_full_name()[:24],  # Device has 24 char limit
                privilege=2 if employee.is_staff else 0,  # Admin or User
                user_id=employee.employee_id
            )
        
        # Update employee sync status
        employee.biometric_synced = True
        employee.biometric_sync_date = timezone.now()
        employee.save()
        
        # Update sync log
        sync_log.status = 'SU'
        sync_log.records_success = 1
        sync_log.completed_at = timezone.now()
        sync_log.save()
        
        logger.info(f"Successfully synced employee {employee.employee_id} to device")
        return {'success': True, 'employee_id': employee.employee_id}
        
    except Employee.DoesNotExist:
        error_msg = f"Employee with ID {employee_id} not found"
        logger.error(error_msg)
        sync_log.error_message = error_msg
        sync_log.records_failed = 1
        sync_log.completed_at = timezone.now()
        sync_log.save()
        return {'success': False, 'error': error_msg}
        
    except Exception as e:
        error_msg = f"Error syncing employee to device: {str(e)}"
        logger.error(error_msg)
        sync_log.error_message = error_msg
        sync_log.records_failed = 1
        sync_log.completed_at = timezone.now()
        sync_log.save()
        
        # Retry the task
        raise self.retry(exc=e, countdown=60)


@shared_task(bind=True)
def sync_attendance_from_device(self):
    """
    Sync TODAY's attendance records from biometric device to database.
    Runs periodically every 5 minutes via Celery Beat.
    Uses TCP-first then UDP-fallback connection (same as manual sync).
    """
    start_time = timezone.now()
    today = start_time.date()

    sync_log = SyncLog.objects.create(
        sync_type='ATTENDANCE_PULL',
        status='FA',
        started_at=start_time,
    )

    records_processed = 0
    records_success = 0
    records_failed = 0

    try:
        with BiometricDeviceService() as device_service:
            if not device_service.conn:
                error_msg = "Could not connect to biometric device (TCP & UDP failed)"
                logger.error(error_msg)
                sync_log.error_message = error_msg
                sync_log.completed_at = timezone.now()
                sync_log.save()
                return {'success': False, 'error': error_msg}

            all_attendances = device_service.get_attendance_records()

        for att in all_attendances:
            try:
                att_time = timezone.make_aware(att.timestamp)
                att_date = att_time.date()

                # Only process today's records
                if att_date != today:
                    continue

                records_processed += 1

                # Robust employee lookup: try employee_id first, then biometric_user_id
                user_id_str = str(att.user_id)
                employee = Employee.objects.filter(employee_id=user_id_str).first()
                if not employee and user_id_str.isdigit():
                    employee = Employee.objects.filter(
                        biometric_user_id=int(user_id_str)
                    ).first()

                if not employee:
                    logger.warning(f"No employee found for biometric user_id={user_id_str}")
                    records_failed += 1
                    continue

                _, created = AttendanceRecord.objects.get_or_create(
                    employee=employee,
                    punch_time=att_time,
                    defaults={
                        'punch_type': 'IN',
                        'biometric_user_id': int(att.uid) if hasattr(att, 'uid') else 0,
                        'punch_state': att.punch,
                        'verify_type': att.status,
                    },
                )

                if created:
                    update_daily_attendance(employee, att_date)

                records_success += 1

            except Exception as e:
                logger.error(f"Error processing attendance record: {str(e)}")
                records_failed += 1
                continue

        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()

        sync_log.status = 'SU' if records_failed == 0 else 'PA'
        sync_log.records_processed = records_processed
        sync_log.records_success = records_success
        sync_log.records_failed = records_failed
        sync_log.completed_at = end_time
        sync_log.duration_seconds = duration
        sync_log.save()

        logger.info(
            f"Auto attendance sync (today={today}): {records_success}/{records_processed} saved, "
            f"{records_failed} failed, {duration:.1f}s"
        )

        return {
            'success': True,
            'date': str(today),
            'records_processed': records_processed,
            'records_success': records_success,
            'records_failed': records_failed,
            'duration': duration,
        }

    except Exception as e:
        error_msg = f"Error syncing attendance from device: {str(e)}"
        logger.error(error_msg)

        end_time = timezone.now()
        duration = (end_time - start_time).total_seconds()

        sync_log.error_message = error_msg
        sync_log.completed_at = end_time
        sync_log.duration_seconds = duration
        sync_log.save()

        return {'success': False, 'error': error_msg}


def update_daily_attendance(employee, date):
    """
    Update or create daily attendance summary for an employee.
    """
    
    # Get attendance records for the day
    records = AttendanceRecord.objects.filter(
        employee=employee,
        punch_time__date=date
    ).order_by('punch_time')
    
    if not records.exists():
        return
    
    # Get or create daily attendance
    daily_att, created = DailyAttendance.objects.get_or_create(
        employee=employee,
        date=date,
        defaults={'status': 'PR'}
    )
    
    # Calculate check-in and check-out times
    first_record = records.first()
    last_record = records.last()
    
    # Convert to local timezone before extracting time
    from django.utils import timezone as tz
    local_tz = tz.get_current_timezone()
    
    daily_att.check_in_time = tz.localtime(first_record.punch_time, local_tz).time()
    daily_att.check_out_time = tz.localtime(last_record.punch_time, local_tz).time() if records.count() > 1 else None
    
    # Calculate total hours
    if daily_att.check_out_time:
        check_in_dt = datetime.combine(date, daily_att.check_in_time)
        check_out_dt = datetime.combine(date, daily_att.check_out_time)
        duration = check_out_dt - check_in_dt
        daily_att.total_hours = round(duration.total_seconds() / 3600, 2)
    
    # Get system settings (consolidated settings)
    try:
        from core.models import SystemSettings
        system_settings = SystemSettings.get_settings()
        
        # Check if late using SystemSettings
        grace_time = datetime.combine(
            date,
            system_settings.office_start_time
        ) + timedelta(minutes=system_settings.late_threshold_minutes)
        
        check_in_dt = datetime.combine(date, daily_att.check_in_time)
        daily_att.is_late = check_in_dt > grace_time
        
        # Check overtime using SystemSettings
        if daily_att.total_hours and daily_att.total_hours > system_settings.overtime_threshold_hours:
            daily_att.is_overtime = True
            daily_att.overtime_hours = daily_att.total_hours - system_settings.overtime_threshold_hours
        
        # Determine status using SystemSettings
        if daily_att.total_hours:
            if daily_att.total_hours < system_settings.half_day_threshold_hours:
                daily_att.status = 'HL'
            elif daily_att.is_late:
                daily_att.status = 'LT'
            else:
                daily_att.status = 'PR'
    except Exception as e:
        logger.warning(f"Error applying attendance settings: {str(e)}")
        pass
    
    daily_att.save()


@shared_task
def sync_all_employees_to_device():
    """
    Sync all active employees to the biometric device.
    """
    employees = Employee.objects.filter(status='AC')
    
    for employee in employees:
        sync_employee_to_device.delay(employee.id)
    
    return {'message': f'Initiated sync for {employees.count()} employees'}


@shared_task
def fetch_device_info():
    """
    Fetch and update device information.
    """
    sync_log = SyncLog.objects.create(
        sync_type='DEVICE_INFO',
        status='FA'
    )
    
    try:
        with BiometricDeviceService() as device_service:
            info = device_service.get_device_info()
            
            # Update or create device record
            device, created = BiometricDevice.objects.get_or_create(
                ip_address=device_service.ip_address,
                defaults={
                    'name': info.get('device_name', 'ZKTeco Device'),
                    'port': device_service.port,
                    'password': device_service.password,
                }
            )
            
            device.serial_number = info.get('serial_number', '')
            device.firmware_version = info.get('firmware_version', '')
            device.platform = info.get('platform', '')
            device.device_name = info.get('device_name', '')
            device.last_connection_status = True
            device.last_sync_time = timezone.now()
            device.save()
        
        sync_log.status = 'SU'
        sync_log.records_success = 1
        sync_log.completed_at = timezone.now()
        sync_log.details = info
        sync_log.save()
        
        return {'success': True, 'info': info}
        
    except Exception as e:
        error_msg = f"Error fetching device info: {str(e)}"
        logger.error(error_msg)
        
        sync_log.error_message = error_msg
        sync_log.completed_at = timezone.now()
        sync_log.save()
        
        return {'success': False, 'error': error_msg}
