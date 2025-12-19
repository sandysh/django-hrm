from rest_framework import serializers
from .models import LeaveType, LeaveRequest, Holiday, LeaveBalance
from employees.serializers import EmployeeListSerializer
from datetime import datetime


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    employee_details = EmployeeListSerializer(source='employee', read_only=True)
    leave_type_details = LeaveTypeSerializer(source='leave_type', read_only=True)
    approved_by_details = EmployeeListSerializer(source='approved_by', read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['total_days', 'approved_at', 'created_at', 'updated_at']
    
    def validate(self, data):
        """
        Validate leave request dates and balance.
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date:
            if end_date < start_date:
                raise serializers.ValidationError("End date must be after start date")
            
            # Calculate total days
            delta = end_date - start_date
            total_days = delta.days + 1
            
            # Check leave balance
            employee = data.get('employee')
            leave_type = data.get('leave_type')
            
            if employee and leave_type:
                current_year = datetime.now().year
                try:
                    balance = LeaveBalance.objects.get(
                        employee=employee,
                        leave_type=leave_type,
                        year=current_year
                    )
                    
                    if balance.balance < total_days:
                        raise serializers.ValidationError(
                            f"Insufficient leave balance. Available: {balance.balance} days"
                        )
                except LeaveBalance.DoesNotExist:
                    raise serializers.ValidationError(
                        "Leave balance not found for this employee and leave type"
                    )
        
        return data


class HolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Holiday
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class LeaveBalanceSerializer(serializers.ModelSerializer):
    employee_details = EmployeeListSerializer(source='employee', read_only=True)
    leave_type_details = LeaveTypeSerializer(source='leave_type', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
        read_only_fields = ['balance', 'created_at', 'updated_at']
