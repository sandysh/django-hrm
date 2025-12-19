import time
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from zk import ZK, const
from employees.models import Employee
from attendance.models import AttendanceRecord
from biometric.tasks import update_daily_attendance

class Command(BaseCommand):
    help = 'Listen for real-time biometric events from the device'

    def handle(self, *args, **options):
        device_ip = settings.BIOMETRIC_DEVICE_IP
        device_port = settings.BIOMETRIC_DEVICE_PORT
        password = settings.BIOMETRIC_DEVICE_PASSWORD
        
        self.stdout.write(self.style.SUCCESS(f'🚀 Starting Live Listener for {device_ip}:{device_port}...'))

        while True:
            conn = None
            zk = None
            try:
                # Initialize ZK
                zk = ZK(device_ip, port=device_port, timeout=10, password=password, force_udp=False, ommit_ping=True)
                
                self.stdout.write('Connecting to device...')
                conn = zk.connect()
                self.stdout.write(self.style.SUCCESS('✅ Connected! Waiting for events...'))
                
                # Start Live Capture Loop
                for event in conn.live_capture():
                    if event is None:
                        # Timeout or keep-alive
                        continue
                        
                    # event.user_id is the string ID of the user on the device
                    # event.timestamp is the datetime
                    # event.punch is the punch state (0=CheckIn, 1=CheckOut, etc - usually 0 or 255 depending on device)
                    
                    self.stdout.write(f"📝 Event Received: User={event.user_id} Time={event.timestamp} Type={event.punch}")
                    
                    self.process_event(event)

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('\n🛑 Stopping listener...'))
                break
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Connection Error: {e}'))
                self.stdout.write('🔄 Reconnecting in 10 seconds...')
                time.sleep(10)
            finally:
                if conn:
                    try:
                        conn.disconnect()
                    except:
                        pass

    def process_event(self, event):
        try:
            # Check if user exists (event.user_id should match employee.employee_id or biometric_user_id)
            # IMPORTANT: When we 'pushed' user, we set user_id=employee_id (String).
            # But specific devices might return the UID (INT) in event.user_id or the User ID string.
            # ZK library usually returns the User ID string in event.user_id.
            
            # Try finding by employee_id first (String match)
            employee = Employee.objects.filter(employee_id=event.user_id).first()
            
            # If not found, try by biometric_user_id (Int match if numeric)
            if not employee and event.user_id.isdigit():
                 employee = Employee.objects.filter(biometric_user_id=int(event.user_id)).first()
            
            if not employee:
                self.stdout.write(self.style.WARNING(f"⚠️ Unknown User ID: {event.user_id}"))
                return

            punch_time = timezone.make_aware(event.timestamp)
            
            # Create Attendance Record
            # We use get_or_create to prevent exact duplicates (same user, same second)
            record, created = AttendanceRecord.objects.get_or_create(
                employee=employee,
                punch_time=punch_time,
                defaults={
                    'punch_type': 'IN', # Logic can be enhanced if device uses states
                    'biometric_user_id': int(event.uid) if hasattr(event, 'uid') else None,
                    'punch_state': event.punch,
                    'verify_type': event.verify_mode if hasattr(event, 'verify_mode') else 0
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ Saved Record: {employee.get_full_name()} at {punch_time.time()}"))
                
                # Update Daily Summary
                update_daily_attendance(employee, punch_time.date())
            else:
                self.stdout.write(f"ℹ️ Duplicate Record ignored")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error processing event: {e}"))
