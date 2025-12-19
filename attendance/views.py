from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count, Q
from datetime import datetime, timedelta
from .models import AttendanceRecord, DailyAttendance, AttendanceSettings
from .serializers import (
    AttendanceRecordSerializer, DailyAttendanceSerializer,
    AttendanceSettingsSerializer, AttendanceSummarySerializer
)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AttendanceRecord CRUD operations.
    """
    queryset = AttendanceRecord.objects.select_related('employee').all()
    serializer_class = AttendanceRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'punch_type', 'is_manual']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['punch_time', 'employee']
    ordering = ['-punch_time']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(punch_time__gte=start_date)
        if end_date:
            queryset = queryset.filter(punch_time__lte=end_date)
        
        return queryset


class DailyAttendanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DailyAttendance CRUD operations.
    """
    queryset = DailyAttendance.objects.select_related('employee').all()
    serializer_class = DailyAttendanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'status', 'is_late', 'is_overtime']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['date', 'employee']
    ordering = ['-date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        Get attendance summary for employees within a date range.
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        employee_id = request.query_params.get('employee_id')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'start_date and end_date are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = DailyAttendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Group by employee and calculate statistics
        summary_data = []
        employees = queryset.values('employee').distinct()
        
        for emp in employees:
            emp_records = queryset.filter(employee_id=emp['employee'])
            employee = emp_records.first().employee
            
            total_days = emp_records.count()
            present_days = emp_records.filter(status='PR').count()
            absent_days = emp_records.filter(status='AB').count()
            half_days = emp_records.filter(status='HL').count()
            late_days = emp_records.filter(is_late=True).count()
            leave_days = emp_records.filter(status='LV').count()
            
            total_hours = emp_records.aggregate(
                total=Sum('total_hours')
            )['total'] or 0
            
            average_hours = emp_records.aggregate(
                avg=Avg('total_hours')
            )['avg'] or 0
            
            overtime_hours = emp_records.aggregate(
                total=Sum('overtime_hours')
            )['total'] or 0
            
            summary_data.append({
                'employee_id': employee.employee_id,
                'employee_name': employee.get_full_name(),
                'total_days': total_days,
                'present_days': present_days,
                'absent_days': absent_days,
                'half_days': half_days,
                'late_days': late_days,
                'leave_days': leave_days,
                'total_hours': round(total_hours, 2),
                'average_hours': round(average_hours, 2),
                'overtime_hours': round(overtime_hours, 2),
            })
        
        serializer = AttendanceSummarySerializer(summary_data, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def sync_from_device(self, request):
        """
        Trigger manual sync of attendance from biometric device.
        """
        from biometric.tasks import sync_attendance_from_device
        task = sync_attendance_from_device.delay()
        
        return Response({
            'message': 'Attendance sync task initiated',
            'task_id': task.id
        }, status=status.HTTP_202_ACCEPTED)


class AttendanceSettingsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for AttendanceSettings.
    """
    queryset = AttendanceSettings.objects.all()
    serializer_class = AttendanceSettingsSerializer
    
    def get_queryset(self):
        # Ensure only one settings instance exists
        settings, created = AttendanceSettings.objects.get_or_create(pk=1)
        return AttendanceSettings.objects.filter(pk=1)
