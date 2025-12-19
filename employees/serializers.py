from rest_framework import serializers
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    """
    Serializer for Employee model.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    total_leave_balance = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone_number', 'date_of_birth', 'gender', 'address',
            'profile_picture', 'department', 'designation', 'employment_type',
            'date_joined_company', 'status', 'biometric_user_id', 'biometric_synced',
            'biometric_sync_date', 'annual_leave_balance', 'sick_leave_balance',
            'casual_leave_balance', 'total_leave_balance', 'is_active', 'is_staff',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['biometric_synced', 'biometric_sync_date', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """
        Create a new employee and trigger biometric sync.
        """
        password = validated_data.pop('password', None)
        employee = Employee(**validated_data)
        
        if password:
            employee.set_password(password)
        
        employee.save()
        
        # Trigger biometric sync task
        from biometric.tasks import sync_employee_to_device
        sync_employee_to_device.delay(employee.id)
        
        return employee
    
    def update(self, instance, validated_data):
        """
        Update employee and trigger biometric sync if necessary.
        """
        password = validated_data.pop('password', None)
        
        # Check if biometric-related fields changed
        biometric_fields_changed = any(
            field in validated_data 
            for field in ['first_name', 'last_name', 'biometric_user_id']
        )
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Trigger biometric sync if relevant fields changed
        if biometric_fields_changed:
            from biometric.tasks import sync_employee_to_device
            sync_employee_to_device.delay(instance.id)
        
        return instance


class EmployeeListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for employee list views.
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    
    class Meta:
        model = Employee
        fields = [
            'id', 'employee_id', 'username', 'full_name', 'email',
            'department', 'designation', 'status', 'biometric_synced'
        ]
