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
