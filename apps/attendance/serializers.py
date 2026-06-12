from rest_framework import serializers
from .models import AttendanceRecord, DailyAttendance
from employees.serializers import EmployeeListSerializer


class AttendanceRecordSerializer(serializers.ModelSerializer):
    employee_details = EmployeeListSerializer(source='employee', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        read_only_fields = ['synced_at']


class DailyAttendanceSerializer(serializers.ModelSerializer):
    employee_details = EmployeeListSerializer(source='employee', read_only=True)
    
    class Meta:
        model = DailyAttendance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class AttendanceSummarySerializer(serializers.Serializer):
    """
    Serializer for attendance summary statistics.
    """
    employee_id = serializers.CharField()
    employee_name = serializers.CharField()
    total_days = serializers.IntegerField()
    present_days = serializers.IntegerField()
    absent_days = serializers.IntegerField()
    half_days = serializers.IntegerField()
    late_days = serializers.IntegerField()
    leave_days = serializers.IntegerField()
    total_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
    average_hours = serializers.DecimalField(max_digits=5, decimal_places=2)
    overtime_hours = serializers.DecimalField(max_digits=10, decimal_places=2)
