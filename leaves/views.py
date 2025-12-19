from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import datetime
from .models import LeaveType, LeaveRequest, Holiday, LeaveBalance
from .serializers import (
    LeaveTypeSerializer, LeaveRequestSerializer,
    HolidaySerializer, LeaveBalanceSerializer
)


class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LeaveType CRUD operations.
    """
    queryset = LeaveType.objects.all()
    serializer_class = LeaveTypeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_paid', 'requires_approval', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'default_days']
    ordering = ['name']


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LeaveRequest CRUD operations.
    """
    queryset = LeaveRequest.objects.select_related('employee', 'leave_type', 'approved_by').all()
    serializer_class = LeaveRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'status']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['start_date', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(start_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(end_date__lte=end_date)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Approve a leave request.
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'PE':
            return Response(
                {'error': 'Only pending requests can be approved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'AP'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.approval_notes = request.data.get('notes', '')
        leave_request.save()
        
        # Update leave balance
        current_year = datetime.now().year
        try:
            balance = LeaveBalance.objects.get(
                employee=leave_request.employee,
                leave_type=leave_request.leave_type,
                year=current_year
            )
            balance.used += leave_request.total_days
            balance.update_balance()
        except LeaveBalance.DoesNotExist:
            pass
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """
        Reject a leave request.
        """
        leave_request = self.get_object()
        
        if leave_request.status != 'PE':
            return Response(
                {'error': 'Only pending requests can be rejected'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'RJ'
        leave_request.approved_by = request.user
        leave_request.approved_at = timezone.now()
        leave_request.approval_notes = request.data.get('notes', '')
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel a leave request.
        """
        leave_request = self.get_object()
        
        if leave_request.status not in ['PE', 'AP']:
            return Response(
                {'error': 'Only pending or approved requests can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # If already approved, restore leave balance
        if leave_request.status == 'AP':
            current_year = datetime.now().year
            try:
                balance = LeaveBalance.objects.get(
                    employee=leave_request.employee,
                    leave_type=leave_request.leave_type,
                    year=current_year
                )
                balance.used -= leave_request.total_days
                balance.update_balance()
            except LeaveBalance.DoesNotExist:
                pass
        
        leave_request.status = 'CA'
        leave_request.save()
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)


class HolidayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Holiday CRUD operations.
    """
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_optional']
    search_fields = ['name']
    ordering_fields = ['date']
    ordering = ['date']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by year
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(date__year=year)
        
        return queryset


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LeaveBalance CRUD operations.
    """
    queryset = LeaveBalance.objects.select_related('employee', 'leave_type').all()
    serializer_class = LeaveBalanceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['employee', 'leave_type', 'year']
    search_fields = ['employee__employee_id', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['year', 'employee']
    ordering = ['-year', 'employee']
    
    @action(detail=False, methods=['post'])
    def initialize_balances(self, request):
        """
        Initialize leave balances for all employees for a given year.
        """
        year = request.data.get('year', datetime.now().year)
        
        from employees.models import Employee
        employees = Employee.objects.filter(status='AC')
        leave_types = LeaveType.objects.filter(is_active=True)
        
        created_count = 0
        for employee in employees:
            for leave_type in leave_types:
                balance, created = LeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type=leave_type,
                    year=year,
                    defaults={
                        'allocated': leave_type.default_days,
                        'used': 0,
                        'balance': leave_type.default_days
                    }
                )
                if created:
                    created_count += 1
        
        return Response({
            'message': f'Initialized {created_count} leave balances for year {year}'
        })
