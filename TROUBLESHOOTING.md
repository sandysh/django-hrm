# Troubleshooting Guide

Common issues and their solutions for the HRM application.

## Table of Contents
1. [Docker Issues](#docker-issues)
2. [Database Issues](#database-issues)
3. [Biometric Device Issues](#biometric-device-issues)
4. [Celery Issues](#celery-issues)
5. [Attendance Sync Issues](#attendance-sync-issues)
6. [Employee Sync Issues](#employee-sync-issues)
7. [API Issues](#api-issues)
8. [Performance Issues](#performance-issues)

---

## Docker Issues

### Issue: Port Already in Use

**Error:**
```
Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use
```

**Solution 1: Find and kill the process**
```bash
# On Mac/Linux
lsof -i :8000
kill -9 <PID>

# On Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**Solution 2: Change the port**
Edit `docker-compose.yml`:
```yaml
web:
  ports:
    - "8001:8000"  # Use port 8001 instead
```

### Issue: Docker Daemon Not Running

**Error:**
```
Cannot connect to the Docker daemon
```

**Solution:**
- Start Docker Desktop
- Or start Docker service:
  ```bash
  # Linux
  sudo systemctl start docker
  
  # Mac
  open -a Docker
  ```

### Issue: Out of Disk Space

**Error:**
```
no space left on device
```

**Solution:**
```bash
# Remove unused images and containers
docker system prune -a

# Remove volumes (WARNING: This deletes data!)
docker system prune -a --volumes
```

---

## Database Issues

### Issue: Database Connection Failed

**Error:**
```
django.db.utils.OperationalError: could not connect to server
```

**Solution 1: Wait for database to be ready**
```bash
# Check database logs
docker-compose logs db

# Wait a bit longer
sleep 10
docker-compose exec web python manage.py migrate
```

**Solution 2: Restart database**
```bash
docker-compose restart db
```

**Solution 3: Check database health**
```bash
docker-compose exec db pg_isready -U hrm_user -d hrm_db
```

### Issue: Migration Conflicts

**Error:**
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Solution:**
```bash
# Reset migrations (WARNING: Development only!)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Issue: Database Locked

**Error:**
```
database is locked
```

**Solution:**
```bash
# This shouldn't happen with PostgreSQL
# If using SQLite in development, switch to PostgreSQL
```

---

## Biometric Device Issues

### Issue: Cannot Connect to Device

**Error:**
```
Failed to connect to device at 192.168.1.201: [Errno 113] No route to host
```

**Diagnosis:**
```bash
# 1. Ping the device
ping 192.168.1.201

# 2. Check if port is accessible
nc -zv 192.168.1.201 4370

# 3. From inside Docker container
docker-compose exec web bash
ping 192.168.1.201
```

**Solutions:**

1. **Wrong IP Address**
   - Verify device IP from device menu
   - Update `.env` file
   - Restart services: `make restart`

2. **Network Isolation**
   - Ensure device is on same network
   - Check firewall rules
   - Try from host machine first

3. **Docker Network Issues**
   - Use host network mode (not recommended for production):
     ```yaml
     web:
       network_mode: "host"
     ```

4. **Device is Off or Unreachable**
   - Check device power
   - Check network cable
   - Restart device

### Issue: Connection Timeout

**Error:**
```
Connection timeout after 5 seconds
```

**Solution:**
```bash
# Increase timeout in .env
BIOMETRIC_DEVICE_TIMEOUT=10

# Restart
make restart
```

### Issue: Wrong Password

**Error:**
```
Authentication failed
```

**Solution:**
```bash
# Try default password
BIOMETRIC_DEVICE_PASSWORD=0

# Or check device settings
# Menu → System → Communication → Password
```

### Issue: Device Returns Empty User List

**Symptoms:** `get_users()` returns empty list

**Solutions:**
1. Check if users exist on device (Menu → User Management)
2. Try re-enrolling a test user
3. Check device firmware version (may need update)
4. Try different pyzk version

---

## Celery Issues

### Issue: Celery Worker Not Running

**Diagnosis:**
```bash
docker-compose ps celery
docker-compose logs celery
```

**Solution:**
```bash
# Restart Celery worker
docker-compose restart celery

# Check for errors in logs
docker-compose logs -f celery
```

### Issue: Celery Beat Not Scheduling Tasks

**Diagnosis:**
```bash
docker-compose logs celery-beat
```

**Solution:**
```bash
# Restart Celery Beat
docker-compose restart celery-beat

# Verify schedule in hrm_project/celery.py
```

### Issue: Tasks Stuck in Queue

**Diagnosis:**
```bash
# Check Redis
docker-compose exec redis redis-cli
> KEYS *
> LLEN celery
```

**Solution:**
```bash
# Clear Redis queue (WARNING: Loses pending tasks!)
docker-compose exec redis redis-cli FLUSHALL

# Restart Celery
docker-compose restart celery celery-beat
```

### Issue: Task Failing Silently

**Solution:**
```bash
# Enable verbose logging
docker-compose logs -f celery

# Check sync logs via API
curl http://localhost:8000/api/biometric/sync-logs/
```

---

## Attendance Sync Issues

### Issue: Attendance Not Syncing

**Symptoms:** Employee punches in/out but no records appear

**Diagnosis Checklist:**
1. ✅ Is Celery Beat running?
2. ✅ Is device connection working?
3. ✅ Does employee have `biometric_user_id`?
4. ✅ Is UID on device matching employee record?
5. ✅ Are there any sync errors in logs?

**Solutions:**

**1. Check Celery Beat**
```bash
docker-compose ps celery-beat
docker-compose logs celery-beat

# Should see: "Scheduler: Sending due task sync-attendance-every-5-minutes"
```

**2. Manual Sync**
```bash
curl -X POST http://localhost:8000/api/attendance/daily/sync_from_device/
```

**3. Check Sync Logs**
```bash
curl http://localhost:8000/api/biometric/sync-logs/ | jq
```

**4. Verify Employee UID**
```bash
# Get employee details
curl http://localhost:8000/api/employees/1/

# Check biometric_user_id matches device UID
```

**5. Check Device Records**
```bash
# Get users from device
curl http://localhost:8000/api/biometric/devices/1/get_users/
```

### Issue: Duplicate Attendance Records

**Symptoms:** Multiple records for same punch time

**Solution:**
```bash
# Check unique_together constraint in AttendanceRecord model
# Should have: unique_together = ['employee', 'punch_time', 'punch_type']

# If duplicates exist, clean them up via Django shell
docker-compose exec web python manage.py shell
```

```python
from attendance.models import AttendanceRecord
from django.db.models import Count

# Find duplicates
duplicates = AttendanceRecord.objects.values(
    'employee', 'punch_time', 'punch_type'
).annotate(count=Count('id')).filter(count__gt=1)

# Remove duplicates (keep first)
for dup in duplicates:
    records = AttendanceRecord.objects.filter(
        employee_id=dup['employee'],
        punch_time=dup['punch_time'],
        punch_type=dup['punch_type']
    ).order_by('id')
    
    # Delete all except first
    records.exclude(id=records.first().id).delete()
```

### Issue: Wrong Work Hours Calculation

**Symptoms:** Daily attendance shows incorrect hours

**Solutions:**

1. **Check Attendance Settings**
   ```bash
   curl http://localhost:8000/api/attendance/settings/
   ```

2. **Verify Check-in/Check-out Times**
   ```bash
   curl "http://localhost:8000/api/attendance/records/?employee=1&start_date=2024-12-18"
   ```

3. **Recalculate Daily Attendance**
   ```python
   # In Django shell
   from attendance.models import DailyAttendance
   from biometric.tasks import update_daily_attendance
   
   # Recalculate for specific date
   daily = DailyAttendance.objects.get(employee_id=1, date='2024-12-18')
   update_daily_attendance(daily.employee, daily.date)
   ```

---

## Employee Sync Issues

### Issue: Employee Not Syncing to Device

**Symptoms:** `biometric_synced=False` after creation

**Diagnosis:**
```bash
# Check Celery worker logs
docker-compose logs celery | grep "sync_employee_to_device"

# Check sync logs
curl http://localhost:8000/api/biometric/sync-logs/?sync_type=USER_PUSH
```

**Solutions:**

**1. Manual Sync**
```bash
curl -X POST http://localhost:8000/api/employees/1/sync_to_biometric/
```

**2. Check Device Connection**
```bash
curl -X POST http://localhost:8000/api/biometric/devices/1/test_connection/
```

**3. Verify UID Assignment**
```bash
curl http://localhost:8000/api/employees/1/ | jq '.biometric_user_id'
```

**4. Check for Errors**
```bash
docker-compose logs celery | grep -A 10 "Error syncing employee"
```

### Issue: UID Already Exists on Device

**Error:**
```
User with UID already exists
```

**Solution:**
```bash
# Assign new UID to employee
# Via Django shell
docker-compose exec web python manage.py shell
```

```python
from employees.models import Employee

emp = Employee.objects.get(id=1)
# Find next available UID
max_uid = Employee.objects.filter(
    biometric_user_id__isnull=False
).order_by('-biometric_user_id').first()

emp.biometric_user_id = max_uid.biometric_user_id + 1
emp.save()

# Trigger sync
from biometric.tasks import sync_employee_to_device
sync_employee_to_device.delay(emp.id)
```

---

## API Issues

### Issue: 401 Unauthorized

**Error:**
```json
{"detail": "Authentication credentials were not provided."}
```

**Solution:**
```bash
# For development, you can disable authentication
# In settings.py:
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Development only!
    ],
}

# Or use session authentication
# Login via admin panel first, then use API
```

### Issue: CORS Errors

**Error:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**Solution:**
```python
# In settings.py
CORS_ALLOW_ALL_ORIGINS = True  # Development only

# For production, specify origins:
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
]
```

### Issue: 500 Internal Server Error

**Diagnosis:**
```bash
# Check Django logs
docker-compose logs web

# Enable DEBUG mode
# In .env:
DEBUG=True
```

---

## Performance Issues

### Issue: Slow API Responses

**Solutions:**

1. **Add Database Indexes**
   ```python
   # In models.py
   class Meta:
       indexes = [
           models.Index(fields=['employee', 'date']),
       ]
   ```

2. **Use select_related/prefetch_related**
   ```python
   # In views.py
   queryset = AttendanceRecord.objects.select_related('employee').all()
   ```

3. **Reduce Page Size**
   ```python
   # In settings.py
   REST_FRAMEWORK = {
       'PAGE_SIZE': 25,  # Reduce from 50
   }
   ```

4. **Add Redis Caching**
   ```python
   # In settings.py
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://redis:6379/1',
       }
   }
   ```

### Issue: High Memory Usage

**Solutions:**

1. **Limit Celery Concurrency**
   ```yaml
   # In docker-compose.yml
   celery:
     command: celery -A hrm_project worker -l info --concurrency=2
   ```

2. **Optimize Queries**
   ```bash
   # Use Django Debug Toolbar in development
   pip install django-debug-toolbar
   ```

3. **Clear Old Sync Logs**
   ```python
   # Create management command to clean old logs
   from datetime import timedelta
   from django.utils import timezone
   from biometric.models import SyncLog
   
   # Delete logs older than 30 days
   cutoff = timezone.now() - timedelta(days=30)
   SyncLog.objects.filter(started_at__lt=cutoff).delete()
   ```

---

## Getting More Help

### Enable Debug Logging

```python
# In settings.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Useful Debug Commands

```bash
# Django shell
make shell

# Database shell
docker-compose exec db psql -U hrm_user hrm_db

# Redis CLI
docker-compose exec redis redis-cli

# View all logs
make logs

# Follow specific service
docker-compose logs -f web
docker-compose logs -f celery
docker-compose logs -f celery-beat

# Execute Django commands
docker-compose exec web python manage.py <command>
```

### Check System Status

```bash
# All services
make ps

# Database health
docker-compose exec db pg_isready

# Redis health
docker-compose exec redis redis-cli ping

# Web health
curl http://localhost:8000/admin/

# API health
curl http://localhost:8000/api/
```

---

## Still Having Issues?

1. Check the logs thoroughly
2. Review the SETUP_GUIDE.md
3. Verify all prerequisites are met
4. Try with a fresh database (development only)
5. Check pyzk library issues: https://github.com/fananimi/pyzk/issues
6. Consult ZKTeco device manual

---

**Last Updated**: December 18, 2024
