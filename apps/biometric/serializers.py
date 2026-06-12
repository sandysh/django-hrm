from rest_framework import serializers
from .models import BiometricDevice, SyncLog


class BiometricDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricDevice
        fields = '__all__'
        read_only_fields = ['serial_number', 'firmware_version', 'platform', 'device_name',
                           'last_sync_time', 'last_connection_status', 'last_error',
                           'created_at', 'updated_at']


class SyncLogSerializer(serializers.ModelSerializer):
    device_details = BiometricDeviceSerializer(source='device', read_only=True)
    
    class Meta:
        model = SyncLog
        fields = '__all__'
        read_only_fields = ['started_at', 'completed_at', 'duration_seconds']


class DeviceStatusSerializer(serializers.Serializer):
    """
    Serializer for device status information.
    """
    connected = serializers.BooleanField()
    device_info = serializers.DictField(required=False)
    error = serializers.CharField(required=False)
