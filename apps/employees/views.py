from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Employee
from .serializers import EmployeeSerializer, EmployeeListSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Employee CRUD operations.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'employment_type', 'department', 'biometric_synced']
    search_fields = ['employee_id', 'username', 'first_name', 'last_name', 'email']
    ordering_fields = ['employee_id', 'created_at', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Use lightweight serializer for list action.
        """
        if self.action == 'list':
            return EmployeeListSerializer
        return EmployeeSerializer
    
    @action(detail=True, methods=['post'])
    def sync_to_biometric(self, request, pk=None):
        """
        Manually trigger sync of employee to biometric device.
        """
        employee = self.get_object()
        
        from biometric.tasks import sync_employee_to_device
        task = sync_employee_to_device.delay(employee.id)
        
        return Response({
            'message': 'Biometric sync task initiated',
            'task_id': task.id,
            'employee_id': employee.employee_id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get employee statistics.
        """
        total_employees = Employee.objects.count()
        active_employees = Employee.objects.filter(status='AC').count()
        synced_employees = Employee.objects.filter(biometric_synced=True).count()
        
        by_department = {}
        for emp in Employee.objects.values('department').distinct():
            dept = emp['department'] or 'Unassigned'
            by_department[dept] = Employee.objects.filter(department=emp['department']).count()
        
        return Response({
            'total_employees': total_employees,
            'active_employees': active_employees,
            'inactive_employees': total_employees - active_employees,
            'biometric_synced': synced_employees,
            'biometric_not_synced': total_employees - synced_employees,
            'by_department': by_department
        })
