# HRM Application - Complete Setup Guide

This guide will walk you through setting up the HRM application with biometric device integration.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Biometric Device Configuration](#biometric-device-configuration)
4. [First-Time Initialization](#first-time-initialization)
5. [Creating Your First Employee](#creating-your-first-employee)
6. [Testing Biometric Integration](#testing-biometric-integration)
7. [Common Issues](#common-issues)

## Prerequisites

### Required Software
- Docker Desktop (or Docker Engine + Docker Compose)
- Git (optional, for version control)
- A text editor (VS Code, Sublime, etc.)

### Network Requirements
- ZKTeco biometric device connected to your network
- Device IP address accessible from your Docker host
- Port 4370 open on the device (default ZKTeco port)

### Finding Your Device IP Address

**Method 1: Using Device Menu**
1. On the device, go to Menu → System → Network
2. Note the IP address displayed

**Method 2: Using Network Scanner**
```bash
# On Linux/Mac
sudo nmap -sn 192.168.1.0/24

# On Windows, use Advanced IP Scanner
```

## Initial Setup

### Step 1: Navigate to Project Directory
```bash
cd /Users/sandy/projects/python/hrm
```

### Step 2: Configure Environment Variables
```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file
nano .env  # or use your preferred editor
```

Update these critical settings in `.env`:
```env
# Django Settings
SECRET_KEY=your-super-secret-key-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Settings (keep defaults for Docker)
DATABASE_URL=postgresql://hrm_user:hrm_password_2024@db:5432/hrm_db

# Biometric Device Settings - UPDATE THESE!
BIOMETRIC_DEVICE_IP=192.168.1.201  # YOUR DEVICE IP
BIOMETRIC_DEVICE_PORT=4370
BIOMETRIC_DEVICE_PASSWORD=0
BIOMETRIC_DEVICE_TIMEOUT=5

# Celery Settings (keep defaults)
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Attendance Sync Interval (in seconds)
ATTENDANCE_SYNC_INTERVAL=300  # 5 minutes
```

### Step 3: Build and Start Services
```bash
# Using Makefile (recommended)
make build
make up

# OR using docker-compose directly
docker-compose build
docker-compose up -d
```

Wait for all services to start (about 30-60 seconds).

### Step 4: Verify Services are Running
```bash
make ps

# You should see 5 services running:
# - hrm_postgres (database)
# - hrm_web (Django application)
# - hrm_celery (background worker)
# - hrm_celery_beat (scheduler)
# - hrm_redis (message broker)
```

### Step 5: Run Database Migrations
```bash
make migrate

# You should see output like:
# Running migrations:
#   Applying contenttypes.0001_initial... OK
#   Applying employees.0001_initial... OK
#   ...
```

### Step 6: Initialize HRM System
```bash
make init

# This creates:
# - Default attendance settings
# - Leave types (Annual, Sick, Casual, etc.)
# - Biometric device configuration
```

### Step 7: Create Admin User
```bash
make createsuperuser

# Follow the prompts:
# Employee ID: ADMIN001
# Username: admin
# Email: admin@example.com
# Password: ********
# Password (again): ********
```

### Step 8: Access the Application
Open your browser and navigate to:
- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/

Login with the credentials you just created.

## Biometric Device Configuration

### Step 1: Test Device Connection

**Via API (using curl)**:
```bash
curl -X POST http://localhost:8000/api/biometric/devices/1/test_connection/ \
  -H "Content-Type: application/json"
```

**Via Admin Panel**:
1. Go to http://localhost:8000/admin
2. Navigate to Biometric → Biometric Devices
3. Click on your device
4. Use the "Test Connection" action

**Expected Response**:
```json
{
  "connected": true,
  "device_info": {
    "firmware_version": "Ver 6.60 Apr 28 2017",
    "serial_number": "BNVR123456789",
    "platform": "ZEM560",
    "device_name": "ZKTeco",
    "mac_address": "00:17:61:12:34:56"
  }
}
```

### Step 2: Troubleshooting Connection Issues

**If connection fails**:

1. **Verify IP address**:
   ```bash
   ping 192.168.1.201
   ```

2. **Check if port is accessible**:
   ```bash
   # On Linux/Mac
   nc -zv 192.168.1.201 4370
   
   # On Windows
   Test-NetConnection -ComputerName 192.168.1.201 -Port 4370
   ```

3. **Check Docker network**:
   ```bash
   # Enter the web container
   make bash
   
   # Try pinging from inside container
   ping 192.168.1.201
   ```

4. **Update device IP in .env**:
   If your device has a different IP, update `.env` and restart:
   ```bash
   make restart
   ```

## First-Time Initialization

### Creating Leave Types (Already Done by init_hrm)

The system comes with these leave types:
- Annual Leave (15 days)
- Sick Leave (10 days)
- Casual Leave (5 days)
- Unpaid Leave
- Maternity Leave (90 days)
- Paternity Leave (7 days)

You can add more via Admin Panel → Leaves → Leave Types

### Configuring Attendance Settings

1. Go to Admin Panel → Attendance → Attendance Settings
2. Adjust settings as needed:
   - Standard work hours: 8.00
   - Shift start time: 09:00:00
   - Shift end time: 17:00:00
   - Grace period: 15 minutes
   - Lunch break: 60 minutes
   - Overtime threshold: 8.00 hours
   - Half day threshold: 4.00 hours

## Creating Your First Employee

### Method 1: Via Admin Panel

1. Go to http://localhost:8000/admin/employees/employee/
2. Click "Add Employee"
3. Fill in required fields:
   - **Employee ID**: EMP001
   - **Username**: john.doe
   - **Email**: john.doe@example.com
   - **First name**: John
   - **Last name**: Doe
   - **Password**: Set a password
   - **Department**: Engineering
   - **Designation**: Software Developer
   - **Employment type**: Full Time
   - **Status**: Active
4. Click "Save"

The system will automatically:
- Assign a biometric UID
- Trigger a sync task to push employee to device
- Mark as `biometric_synced=True` when complete

### Method 2: Via API

```bash
curl -X POST http://localhost:8000/api/employees/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "username": "john.doe",
    "email": "john.doe@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "secure_password_123",
    "department": "Engineering",
    "designation": "Software Developer",
    "employment_type": "FT",
    "status": "AC"
  }'
```

### Verify Employee Synced to Device

**Check sync status**:
```bash
# View employee details
curl http://localhost:8000/api/employees/1/

# Check sync logs
curl http://localhost:8000/api/biometric/sync-logs/
```

**Check on device**:
1. On biometric device, go to Menu → User Management
2. You should see "John Doe" in the user list

## Testing Biometric Integration

### Test 1: Manual Employee Sync

```bash
# Sync specific employee
curl -X POST http://localhost:8000/api/employees/1/sync_to_biometric/

# Sync all employees
curl -X POST http://localhost:8000/api/biometric/devices/1/sync_users/
```

### Test 2: Attendance Recording

1. **Record attendance on device**:
   - Have employee place finger on biometric device
   - Device should beep and show "Thank You"

2. **Wait for sync** (or trigger manually):
   ```bash
   # Manual sync
   curl -X POST http://localhost:8000/api/attendance/daily/sync_from_device/
   
   # Or wait 5 minutes for automatic sync
   ```

3. **Check attendance records**:
   ```bash
   # View all attendance records
   curl http://localhost:8000/api/attendance/records/
   
   # View daily attendance
   curl http://localhost:8000/api/attendance/daily/
   ```

### Test 3: Attendance Summary

```bash
# Get attendance summary for date range
curl "http://localhost:8000/api/attendance/daily/summary/?start_date=2024-01-01&end_date=2024-12-31"
```

## Initializing Leave Balances

After creating employees, initialize their leave balances:

```bash
curl -X POST http://localhost:8000/api/leaves/balances/initialize_balances/ \
  -H "Content-Type: application/json" \
  -d '{"year": 2024}'
```

This will create leave balance records for all active employees based on leave type defaults.

## Common Issues

### Issue 1: Employee Not Syncing to Device

**Symptoms**: Employee created but `biometric_synced=False`

**Solutions**:
1. Check Celery worker logs:
   ```bash
   make logs-celery
   ```

2. Verify device connection:
   ```bash
   curl -X POST http://localhost:8000/api/biometric/devices/1/test_connection/
   ```

3. Manually trigger sync:
   ```bash
   curl -X POST http://localhost:8000/api/employees/1/sync_to_biometric/
   ```

### Issue 2: Attendance Not Syncing

**Symptoms**: Employee punches in/out but no records in system

**Solutions**:
1. Check if Celery Beat is running:
   ```bash
   make logs-beat
   ```

2. Verify employee has `biometric_user_id`:
   ```bash
   curl http://localhost:8000/api/employees/1/
   ```

3. Check sync logs for errors:
   ```bash
   curl http://localhost:8000/api/biometric/sync-logs/
   ```

4. Manually trigger sync:
   ```bash
   curl -X POST http://localhost:8000/api/attendance/daily/sync_from_device/
   ```

### Issue 3: Database Connection Error

**Symptoms**: "could not connect to server"

**Solutions**:
1. Wait for database to be ready:
   ```bash
   docker-compose logs db
   ```

2. Restart services:
   ```bash
   make restart
   ```

3. Check database health:
   ```bash
   docker-compose exec db pg_isready -U hrm_user
   ```

### Issue 4: Port Already in Use

**Symptoms**: "port 8000 is already allocated"

**Solutions**:
1. Stop conflicting service:
   ```bash
   # Find process using port 8000
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   ```

2. Or change port in docker-compose.yml:
   ```yaml
   ports:
     - "8001:8000"  # Use port 8001 instead
   ```

## Next Steps

1. **Create more employees** and test biometric sync
2. **Configure holidays** for the year
3. **Set up leave balances** for all employees
4. **Test leave request workflow**
5. **Monitor attendance** for a few days
6. **Review sync logs** regularly
7. **Set up backups** (see README.md)

## Getting Help

- Check logs: `make logs`
- View sync logs: Admin Panel → Biometric → Sync Logs
- Test device connection regularly
- Monitor Celery tasks for errors

## Production Deployment

Before deploying to production:

1. ✅ Change `SECRET_KEY` to a strong random value
2. ✅ Set `DEBUG=False`
3. ✅ Update `ALLOWED_HOSTS` with your domain
4. ✅ Use strong database passwords
5. ✅ Enable HTTPS/SSL
6. ✅ Set up regular database backups
7. ✅ Configure firewall rules
8. ✅ Set up monitoring and alerting
9. ✅ Review and adjust Celery task schedules
10. ✅ Test disaster recovery procedures

---

**Congratulations!** Your HRM system with biometric integration is now set up and ready to use! 🎉
