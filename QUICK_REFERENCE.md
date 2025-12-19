# HRM Application - Quick Reference

## 🚀 Quick Start

```bash
# 1. Navigate to project
cd /Users/sandy/projects/python/hrm

# 2. Run quick start script
./quickstart.sh

# OR manually:
cp .env.example .env
# Edit .env to set your device IP
make build
make up
make migrate
make init
make createsuperuser
```

## 📱 Access Points

- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/
- **Employees**: http://localhost:8000/api/employees/
- **Attendance**: http://localhost:8000/api/attendance/
- **Leaves**: http://localhost:8000/api/leaves/
- **Biometric**: http://localhost:8000/api/biometric/

## 🔧 Common Commands

```bash
# Start application
make up

# Stop application
make down

# View logs
make logs
make logs-web
make logs-celery

# Database operations
make migrate
make makemigrations
make backup-db

# Django operations
make shell
make createsuperuser
make collectstatic

# Initialize system
make init
```

## 📋 Environment Variables

**Critical Settings in `.env`:**
```env
BIOMETRIC_DEVICE_IP=192.168.1.201  # ⚠️ UPDATE THIS!
BIOMETRIC_DEVICE_PORT=4370
BIOMETRIC_DEVICE_PASSWORD=0
ATTENDANCE_SYNC_INTERVAL=300
```

## 🔄 Workflow Examples

### Create Employee
```bash
curl -X POST http://localhost:8000/api/employees/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP001",
    "username": "john.doe",
    "email": "john@example.com",
    "password": "password123",
    "first_name": "John",
    "last_name": "Doe",
    "department": "Engineering",
    "designation": "Developer",
    "employment_type": "FT",
    "status": "AC"
  }'
```

### Test Device Connection
```bash
curl -X POST http://localhost:8000/api/biometric/devices/1/test_connection/
```

### Sync Attendance
```bash
curl -X POST http://localhost:8000/api/attendance/daily/sync_from_device/
```

### Get Attendance Summary
```bash
curl "http://localhost:8000/api/attendance/daily/summary/?start_date=2024-01-01&end_date=2024-12-31"
```

### Submit Leave Request
```bash
curl -X POST http://localhost:8000/api/leaves/requests/ \
  -H "Content-Type: application/json" \
  -d '{
    "employee": 1,
    "leave_type": 1,
    "start_date": "2024-12-20",
    "end_date": "2024-12-22",
    "reason": "Family vacation"
  }'
```

### Approve Leave
```bash
curl -X POST http://localhost:8000/api/leaves/requests/1/approve/ \
  -H "Content-Type: application/json" \
  -d '{"notes": "Approved"}'
```

## 🔍 Troubleshooting Quick Checks

```bash
# Check all services
make ps

# Check device connectivity
ping 192.168.1.201

# Check sync logs
curl http://localhost:8000/api/biometric/sync-logs/

# Check Celery Beat
docker-compose logs celery-beat | grep "sync-attendance"

# Restart everything
make restart
```

## 📚 Documentation Files

- **README.md** - Main overview and features
- **SETUP_GUIDE.md** - Detailed setup instructions
- **API_DOCUMENTATION.md** - Complete API reference
- **PROJECT_STRUCTURE.md** - Architecture and code organization
- **TROUBLESHOOTING.md** - Common issues and solutions

## ⚙️ Key Features

✅ Employee management with biometric sync
✅ Automatic attendance tracking (every 5 min)
✅ Leave request workflow
✅ Daily attendance summaries
✅ Work hours & overtime calculation
✅ Leave balance management
✅ Holiday calendar
✅ Comprehensive API
✅ Docker-based deployment
✅ Background task processing

## 🎯 Next Steps After Setup

1. ✅ Test biometric device connection
2. ✅ Create first employee
3. ✅ Verify employee synced to device
4. ✅ Test attendance punch on device
5. ✅ Wait for sync or trigger manually
6. ✅ Check attendance records
7. ✅ Initialize leave balances
8. ✅ Test leave request workflow
9. ✅ Configure holidays
10. ✅ Monitor sync logs

## ⚠️ Important Notes

- **Device IP**: Must update in `.env` before starting
- **Sync Interval**: Default 5 minutes, configurable
- **Biometric UID**: Auto-assigned, must be unique
- **Leave Balance**: Must initialize for each year
- **Attendance Settings**: Configure work hours and policies
- **Production**: Change SECRET_KEY, set DEBUG=False

## 🆘 Getting Help

1. Check logs: `make logs`
2. Review TROUBLESHOOTING.md
3. Test device connection
4. Verify Celery is running
5. Check sync logs via API

## 📞 Support Resources

- **pyzk Library**: https://github.com/fananimi/pyzk
- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/

---

**Version**: 1.0.0  
**Last Updated**: December 18, 2024  
**Python**: 3.11  
**Django**: 4.2.8
