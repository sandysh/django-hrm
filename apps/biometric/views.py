from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from .models import BiometricDevice, SyncLog
from .serializers import BiometricDeviceSerializer, SyncLogSerializer, DeviceStatusSerializer
from .services import BiometricDeviceService
from .tasks import (
    sync_employee_to_device, sync_attendance_from_device,
    sync_all_employees_to_device, fetch_device_info
)
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
import time

from employees.models import Employee, Department
from attendance.models import AttendanceRecord
from .models import BiometricDevice, SyncLog
from .services import BiometricDeviceService


class BiometricDeviceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for BiometricDevice CRUD operations.
    """
    queryset = BiometricDevice.objects.all()
    serializer_class = BiometricDeviceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'last_connection_status']
    search_fields = ['name', 'ip_address', 'serial_number']
    ordering_fields = ['name', 'last_sync_time']
    ordering = ['-last_sync_time']
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """
        Test connection to a biometric device.
        """
        device = self.get_object()
        
        try:
            with BiometricDeviceService(
                ip_address=device.ip_address,
                port=device.port,
                password=device.password,
                timeout=device.timeout
            ) as service:
                info = service.get_device_info()
                
                # Update device info
                device.serial_number = info.get('serial_number', '')
                device.firmware_version = info.get('firmware_version', '')
                device.platform = info.get('platform', '')
                device.device_name = info.get('device_name', '')
                device.last_connection_status = True
                device.last_error = ''
                device.save()
                
                return Response({
                    'connected': True,
                    'device_info': info
                })
        except Exception as e:
            device.last_connection_status = False
            device.last_error = str(e)
            device.save()
            
            return Response({
                'connected': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sync_users(self, request, pk=None):
        """
        Sync all employees to this device.
        """
        device = self.get_object()
        task = sync_all_employees_to_device.delay()
        
        return Response({
            'message': 'User sync task initiated',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def sync_attendance(self, request, pk=None):
        """
        Sync attendance from this device.
        """
        device = self.get_object()
        task = sync_attendance_from_device.delay()
        
        return Response({
            'message': 'Attendance sync task initiated',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['post'])
    def fetch_info(self, request, pk=None):
        """
        Fetch device information.
        """
        device = self.get_object()
        task = fetch_device_info.delay()
        
        return Response({
            'message': 'Device info fetch task initiated',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['get'])
    def get_users(self, request, pk=None):
        """
        Get all users from the device.
        """
        device = self.get_object()
        
        try:
            with BiometricDeviceService(
                ip_address=device.ip_address,
                port=device.port,
                password=device.password,
                timeout=device.timeout
            ) as service:
                users = service.get_users()
                
                user_list = []
                for user in users:
                    user_list.append({
                        'uid': user.uid,
                        'name': user.name,
                        'privilege': user.privilege,
                        'user_id': user.user_id,
                        'group_id': user.group_id,
                    })
                
                return Response({
                    'total_users': len(user_list),
                    'users': user_list
                })
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class SyncLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for SyncLog read operations.
    """
    queryset = SyncLog.objects.all()
    serializer_class = SyncLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['sync_type', 'status', 'device']
    ordering_fields = ['started_at', 'duration_seconds']
    ordering = ['-started_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(started_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(started_at__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get sync statistics.
        """
        from django.db.models import Count, Avg, Sum
        
        stats = SyncLog.objects.aggregate(
            total_syncs=Count('id'),
            successful_syncs=Count('id', filter=models.Q(status='SU')),
            failed_syncs=Count('id', filter=models.Q(status='FA')),
            partial_syncs=Count('id', filter=models.Q(status='PA')),
            avg_duration=Avg('duration_seconds'),
            total_records_processed=Sum('records_processed'),
            total_records_success=Sum('records_success'),
            total_records_failed=Sum('records_failed'),
        )
        
        return Response(stats)


class DumpBiometricDataView(LoginRequiredMixin, UserPassesTestMixin, View):
    """
    Dumps ALL data from biometric device to local DB.
    Step 1: Sync users  → creates/updates Employee records
    Step 2: Sync attendance → creates AttendanceRecord records
    Logs everything to SyncLog.
    """

    def test_func(self):
        return self.request.user.is_staff

    def get(self, request, pk=None):
        # Get device — use pk from URL or fall back to first active device
        if pk:
            device = get_object_or_404(BiometricDevice, pk=pk, is_active=True)
        else:
            device = BiometricDevice.objects.filter(is_active=True).first()
            if not device:
                messages.error(request, "No active biometric device configured.")
                return redirect('dashboard')

        now = timezone.now()
        started_at = time.time()

        # ── Step 1: Sync Departments ─────────────────────────────────────────
        dept_log = SyncLog.objects.create(
            device=device,
            sync_type='DEPARTMENT_PULL',
            status='PA',  # mark partial until done
        )

        depts_created = 0
        depts_found = 0
        depts_failed = 0
        group_id_map = {}  # Map group_id → department

        try:
            with BiometricDeviceService(
                ip_address=device.ip_address,
                port=device.port,
                password=device.password,
                timeout=device.timeout,
            ) as service:
                
                users = service.get_users()
                print(f"[DUMP] {len(users)} users on device")
                
                # Collect unique group_ids
                group_ids = set()
                for user in users:
                    if hasattr(user, 'group_id') and user.group_id:
                        group_ids.add(str(user.group_id).strip())
                
                print(f"[DUMP] Found {len(group_ids)} unique departments/groups: {group_ids}")
                
                # Create or get departments for each group_id
                for group_id in group_ids:
                    try:
                        if not group_id or group_id == '0':
                            continue
                        
                        dept, created = Department.objects.get_or_create(
                            code=group_id,
                            defaults={
                                'name': f'Dept_{group_id}',
                                'description': f'Auto-synced from biometric device group {group_id}',
                                'is_active': True,
                            }
                        )
                        
                        group_id_map[group_id] = dept
                        
                        if created:
                            depts_created += 1
                            print(f"[DUMP] Created department: {dept.name} (code={group_id})")
                        else:
                            depts_found += 1
                            print(f"[DUMP] Found existing department: {dept.name} (code={group_id})")
                    
                    except Exception as e:
                        depts_failed += 1
                        print(f"[DUMP] Failed to create/get department code={group_id}: {e}")
            
            dept_log.status = 'FA' if depts_failed == len(group_ids) else ('SU' if depts_failed == 0 else 'PA')
            dept_log.records_processed = len(group_ids)
            dept_log.records_success = depts_created + depts_found
            dept_log.records_failed = depts_failed
            dept_log.completed_at = timezone.now()
            dept_log.duration_seconds = round(time.time() - started_at, 2)
            dept_log.details = {
                'created': depts_created,
                'found': depts_found,
                'failed': depts_failed,
            }
            dept_log.save()
            print(f"[DUMP] Department sync complete — {depts_created} created, {depts_found} found")
        
        except Exception as e:
            dept_log.status = 'FA'
            dept_log.error_message = str(e)
            dept_log.completed_at = timezone.now()
            dept_log.save()
            messages.error(request, f"Department sync failed: {e}")
            return redirect('dashboard')

        # ── Step 2: Sync Users ───────────────────────────────────────────────
        user_log = SyncLog.objects.create(
            device=device,
            sync_type='USER_PULL',
            status='PA',  # mark partial until done
        )

        users_created = 0
        users_updated = 0
        users_failed = 0

        try:
            with BiometricDeviceService(
                ip_address=device.ip_address,
                port=device.port,
                password=device.password,
                timeout=device.timeout,
            ) as service:

                users = service.get_users()
                print(f"[DUMP] {len(users)} users on device")

                for user in users:
                    try:
                        if not user.uid:
                            continue

                        name_parts = (user.name or '').split(' ', 1)
                        first_name = name_parts[0]
                        last_name = name_parts[1] if len(name_parts) > 1 else ''

                        # Get department for this user based on group_id
                        user_department = None
                        if hasattr(user, 'group_id') and user.group_id:
                            user_department = group_id_map.get(str(user.group_id).strip())

                        employee, created = Employee.objects.get_or_create(
                            biometric_user_id=int(user.uid),
                            defaults={
                                'username': f"bio_{user.uid}",
                                'employee_id': str(user.user_id) if user.user_id else f"BIO{int(user.uid):03d}",
                                'first_name': first_name,
                                'last_name': last_name,
                                'biometric_synced': True,
                                'biometric_sync_date': now,
                                'department': user_department,
                            }
                        )

                        if created:
                            users_created += 1
                            print(f"[DUMP] Created: uid={user.uid} name={user.name} dept={user_department}")
                        else:
                            # Update name/sync status if missing
                            updated_fields = []
                            if not employee.first_name and first_name:
                                employee.first_name = first_name
                                employee.last_name = last_name
                                updated_fields += ['first_name', 'last_name']
                            if not employee.biometric_synced:
                                employee.biometric_synced = True
                                employee.biometric_sync_date = now
                                updated_fields += ['biometric_synced', 'biometric_sync_date']
                            if not employee.department and user_department:
                                employee.department = user_department
                                updated_fields += ['department']
                            if updated_fields:
                                employee.save(update_fields=updated_fields)
                                users_updated += 1

                    except Exception as e:
                        users_failed += 1
                        print(f"[DUMP] Failed to create user uid={getattr(user, 'uid', '?')}: {e}")

            user_log.status = 'FA' if users_failed == len(users) else ('SU' if users_failed == 0 else 'PA')
            user_log.records_processed = len(users)
            user_log.records_success = users_created + users_updated
            user_log.records_failed = users_failed
            user_log.completed_at = timezone.now()
            user_log.duration_seconds = round(time.time() - started_at, 2)
            user_log.details = {
                'created': users_created,
                'updated': users_updated,
                'failed': users_failed,
            }
            user_log.save()

        except Exception as e:
            user_log.status = 'FA'
            user_log.error_message = str(e)
            user_log.completed_at = timezone.now()
            user_log.save()
            messages.error(request, f"User sync failed: {e}")
            return redirect('dashboard')

        # ── Step 3: Sync Attendance ──────────────────────────────────────────
        att_log = SyncLog.objects.create(
            device=device,
            sync_type='ATTENDANCE_PULL',
            status='PA',
        )

        att_started = time.time()
        attendance_created = 0
        attendance_skipped = 0
        attendance_failed = 0
        unmatched = set()

        try:
            # Build lookup from what we just synced
            employee_lookup = {
                emp.biometric_user_id: emp
                for emp in Employee.objects.filter(biometric_user_id__isnull=False)
            }
            print(f"[DUMP] Lookup ready — {len(employee_lookup)} employees")

            with BiometricDeviceService(
                ip_address=device.ip_address,
                port=device.port,
                password=device.password,
                timeout=device.timeout,
            ) as service:

                attendances = service.get_attendance_records()
                print(f"[DUMP] {len(attendances)} attendance logs on device")

                for att in attendances:
                    try:
                        uid = int(att.uid) if hasattr(att, 'uid') and att.uid else None
                        if uid is None:
                            attendance_failed += 1
                            continue

                        employee = employee_lookup.get(uid)
                        if not employee:
                            unmatched.add(str(uid))
                            attendance_skipped += 1
                            continue

                        att_time = timezone.make_aware(att.timestamp)

                        _, created = AttendanceRecord.objects.get_or_create(
                            employee=employee,
                            punch_time=att_time,
                            defaults={
                                'punch_type': 'IN',
                                'biometric_user_id': uid,
                                'punch_state': att.punch,
                                'verify_type': att.status,
                            }
                        )

                        if created:
                            attendance_created += 1
                        else:
                            attendance_skipped += 1

                    except Exception as e:
                        attendance_failed += 1
                        print(f"[DUMP] Attendance error uid={getattr(att, 'uid', '?')}: {e}")

            att_log.status = 'FA' if attendance_failed == len(attendances) else ('SU' if attendance_failed == 0 else 'PA')
            att_log.records_processed = len(attendances)
            att_log.records_success = attendance_created
            att_log.records_failed = attendance_failed
            att_log.completed_at = timezone.now()
            att_log.duration_seconds = round(time.time() - att_started, 2)
            att_log.details = {
                'created': attendance_created,
                'skipped_duplicates': attendance_skipped,
                'failed': attendance_failed,
                'unmatched_uids': sorted(unmatched),
            }
            att_log.save()

            # Update device last sync time
            device.last_sync_time = timezone.now()
            device.last_connection_status = True
            device.last_error = ''
            device.save(update_fields=['last_sync_time', 'last_connection_status', 'last_error'])

        except Exception as e:
            att_log.status = 'FA'
            att_log.error_message = str(e)
            att_log.completed_at = timezone.now()
            att_log.save()
            device.last_connection_status = False
            device.last_error = str(e)
            device.save(update_fields=['last_connection_status', 'last_error'])
            messages.error(request, f"Attendance sync failed: {e}")
            return redirect('dashboard')

        messages.success(
            request,
            f"Dump complete — "
            f"{depts_created} new departments | "
            f"{users_created} new employees, {users_updated} updated | "
            f"{attendance_created} new attendance records"
            + (f" | Unmatched uids: {', '.join(sorted(unmatched))}" if unmatched else "")
        )
        return redirect('dashboard')
    
    
    