"""
Service layer for interacting with ZKTeco biometric devices using pyzk library.
"""
import logging
from typing import Optional, List, Dict, Tuple
from datetime import datetime
from django.conf import settings
from zk import ZK, const
from zk.user import User
from zk.attendance import Attendance

logger = logging.getLogger(__name__)


class BiometricDeviceService:
    """
    Service class to handle all interactions with ZKTeco biometric devices.
    """
    
    def __init__(self, ip_address: str = None, port: int = None, 
                 password: int = None, timeout: int = None):
        """
        Initialize the biometric device service.
        """
        self.ip_address = ip_address or settings.BIOMETRIC_DEVICE_IP
        self.port = port or settings.BIOMETRIC_DEVICE_PORT
        self.password = password or settings.BIOMETRIC_DEVICE_PASSWORD
        self.timeout = timeout or settings.BIOMETRIC_DEVICE_TIMEOUT
        
        self.zk = ZK(
            self.ip_address,
            port=self.port,
            timeout=self.timeout,
            password=self.password,
            force_udp=False,
            ommit_ping=False
        )
        self.conn = None
    
    def connect(self) -> bool:
        """
        Connect to the biometric device.
        Tries TCP first, then falls back to UDP (mirrors manual sync behaviour).
        """
        # Try TCP first
        try:
            zk = ZK(
                self.ip_address,
                port=self.port,
                timeout=self.timeout,
                password=self.password,
                force_udp=False,
                ommit_ping=True,
            )
            self.conn = zk.connect()
            logger.info(f"Connected to device at {self.ip_address} via TCP")
            return True
        except Exception:
            pass

        # Fallback to UDP
        try:
            zk = ZK(
                self.ip_address,
                port=self.port,
                timeout=self.timeout,
                password=self.password,
                force_udp=True,
                ommit_ping=True,
            )
            self.conn = zk.connect()
            logger.info(f"Connected to device at {self.ip_address} via UDP")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to device at {self.ip_address} (TCP & UDP): {str(e)}")
            return False
    
    def disconnect(self):
        """
        Disconnect from the biometric device.
        """
        if self.conn:
            try:
                self.conn.disconnect()
                logger.info(f"Disconnected from device at {self.ip_address}")
            except Exception as e:
                logger.error(f"Error disconnecting from device: {str(e)}")
    
    def get_device_info(self) -> Dict:
        """
        Get device information.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            info = {
                'firmware_version': self.conn.get_firmware_version(),
                'serial_number': self.conn.get_serialnumber(),
                'platform': self.conn.get_platform(),
                'device_name': self.conn.get_device_name(),
                'mac_address': self.conn.get_mac(),
            }
            logger.info(f"Retrieved device info: {info}")
            return info
        except Exception as e:
            logger.error(f"Error getting device info: {str(e)}")
            raise
    
    def get_users(self) -> List[User]:
        """
        Get all users from the device.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.disable_device()
            users = self.conn.get_users()
            self.conn.enable_device()
            logger.info(f"Retrieved {len(users)} users from device")
            return users
        except Exception as e:
            logger.error(f"Error getting users from device: {str(e)}")
            self.conn.enable_device()
            raise
    
    def create_user(self, uid: int, name: str, privilege: int = const.USER_DEFAULT,
                   password: str = '', group_id: str = '', user_id: str = '') -> bool:
        """
        Create a user on the biometric device.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.disable_device()
            self.conn.set_user(
                uid=uid,
                name=name,
                privilege=privilege,
                password=password,
                group_id=group_id,
                user_id=user_id,
                card=0
            )
            self.conn.enable_device()
            logger.info(f"Created user {name} (UID: {uid}) on device")
            return True
        except Exception as e:
            logger.error(f"Error creating user on device: {str(e)}")
            self.conn.enable_device()
            raise
    
    def update_user(self, uid: int, name: str, privilege: int = const.USER_DEFAULT,
                   password: str = '', group_id: str = '', user_id: str = '') -> bool:
        """
        Update a user on the biometric device.
        """
        # In pyzk, updating is the same as creating (it overwrites)
        return self.create_user(uid, name, privilege, password, group_id, user_id)
    
    def delete_user(self, uid: int) -> bool:
        """
        Delete a user from the biometric device.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.disable_device()
            self.conn.delete_user(uid=uid)
            self.conn.enable_device()
            logger.info(f"Deleted user UID: {uid} from device")
            return True
        except Exception as e:
            logger.error(f"Error deleting user from device: {str(e)}")
            self.conn.enable_device()
            raise
    
    def get_attendance_records(self) -> List[Attendance]:
        """
        Get all attendance records from the device.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.disable_device()
            attendances = self.conn.get_attendance()
            self.conn.enable_device()
            logger.info(f"Retrieved {len(attendances)} attendance records from device")
            return attendances
        except Exception as e:
            logger.error(f"Error getting attendance records from device: {str(e)}")
            self.conn.enable_device()
            raise
    
    def clear_attendance_records(self) -> bool:
        """
        Clear all attendance records from the device.
        WARNING: This will delete all attendance data from the device!
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.disable_device()
            self.conn.clear_attendance()
            self.conn.enable_device()
            logger.info("Cleared all attendance records from device")
            return True
        except Exception as e:
            logger.error(f"Error clearing attendance records: {str(e)}")
            self.conn.enable_device()
            raise
    
    def test_voice(self, index: int = 0) -> bool:
        """
        Test device voice/sound.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.test_voice(index=index)
            logger.info(f"Played test voice with index {index}")
            return True
        except Exception as e:
            logger.error(f"Error playing test voice: {str(e)}")
            raise
    
    def get_device_time(self) -> datetime:
        """
        Get current time from the device.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            device_time = self.conn.get_time()
            logger.info(f"Device time: {device_time}")
            return device_time
        except Exception as e:
            logger.error(f"Error getting device time: {str(e)}")
            raise
    
    def set_device_time(self, new_time: datetime) -> bool:
        """
        Set device time.
        """
        if not self.conn:
            raise Exception("Not connected to device")
        
        try:
            self.conn.set_time(new_time)
            logger.info(f"Set device time to {new_time}")
            return True
        except Exception as e:
            logger.error(f"Error setting device time: {str(e)}")
            raise
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
