# HRM Application with Biometric Integration

A comprehensive Human Resource Management (HRM) application built with Django and PostgreSQL, featuring ZKTeco biometric device integration for automated attendance tracking.

## Features

### 🧑‍💼 Employee Management
- Complete employee profile management
- Custom employee ID system
- Department and designation tracking
- Employment type classification (Full-time, Part-time, Contract, Intern)
- Employee status management (Active, Inactive, Suspended, Terminated)
- Profile pictures and personal information
- Automatic biometric device synchronization

### 📊 Attendance Management
- Real-time attendance tracking from biometric devices
- Automatic attendance record synchronization (every 5 minutes)
- Daily attendance summaries with work hours calculation
- Late arrival and early departure tracking
- Overtime calculation
- Configurable attendance policies (grace period, shift timings, etc.)
- Attendance statistics and reports

### 🏖️ Leave Management
- Multiple leave types (Annual, Sick, Casual, etc.)
- Leave request submission and approval workflow
- Leave balance tracking per employee
- Holiday calendar management
- Leave request validation against available balance
- Automatic leave balance deduction on approval

### 🔐 Biometric Device Integration
- ZKTeco device connectivity via pyzk library
- Automatic employee synchronization to device
- Real-time attendance data pull from device
- Device status monitoring
- Sync logs and error tracking
- Support for multiple biometric devices
- Device information retrieval (firmware, serial number, etc.)

## Technology Stack

- **Backend**: Django 4.2.8
- **Database**: PostgreSQL 15
- **Task Queue**: Celery with Redis
- **Biometric Library**: pyzk 0.9
- **API**: Django REST Framework
- **Containerization**: Docker & Docker Compose

## Prerequisites

- Docker and Docker Compose installed
- ZKTeco biometric device accessible on your network
- Device IP address (default: 192.168.1.201)

## Quick Start

### 1. Clone and Setup

```bash
cd /Users/sandy/projects/python/hrm
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` file and update the biometric device settings:

```env
BIOMETRIC_DEVICE_IP=192.168.1.201  # Your device IP
BIOMETRIC_DEVICE_PORT=4370
BIOMETRIC_DEVICE_PASSWORD=0
```

### 3. Build and Run with Docker Compose

```bash
# Build and start all services
docker-compose up -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f web
```

### 4. Initialize Database

```bash
# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Initialize attendance settings
docker-compose exec web python manage.py shell
```

In the Django shell:
```python
from attendance.models import AttendanceSettings
AttendanceSettings.objects.create(
    standard_work_hours=8.00,
    shift_start_time='09:00:00',
    shift_end_time='17:00:00',
    grace_period_minutes=15
)
exit()
```

### 5. Access the Application

- **Admin Panel**: http://localhost:8000/admin
- **API Root**: http://localhost:8000/api/
- **Employees API**: http://localhost:8000/api/employees/
- **Attendance API**: http://localhost:8000/api/attendance/
- **Leaves API**: http://localhost:8000/api/leaves/
- **Biometric API**: http://localhost:8000/api/biometric/

## API Endpoints

### Employee Management
- `GET /api/employees/` - List all employees
- `POST /api/employees/` - Create new employee (auto-syncs to device)
- `GET /api/employees/{id}/` - Get employee details
- `PUT /api/employees/{id}/` - Update employee
- `DELETE /api/employees/{id}/` - Delete employee
- `POST /api/employees/{id}/sync_to_biometric/` - Manual sync to device
- `GET /api/employees/statistics/` - Get employee statistics

### Attendance Management
- `GET /api/attendance/records/` - List attendance records
- `GET /api/attendance/daily/` - List daily attendance summaries
- `GET /api/attendance/daily/summary/` - Get attendance summary with statistics
- `POST /api/attendance/daily/sync_from_device/` - Manual sync from device
- `GET /api/attendance/settings/` - Get attendance settings

### Leave Management
- `GET /api/leaves/types/` - List leave types
- `POST /api/leaves/types/` - Create leave type
- `GET /api/leaves/requests/` - List leave requests
- `POST /api/leaves/requests/` - Submit leave request
- `POST /api/leaves/requests/{id}/approve/` - Approve leave request
- `POST /api/leaves/requests/{id}/reject/` - Reject leave request
- `POST /api/leaves/requests/{id}/cancel/` - Cancel leave request
- `GET /api/leaves/balances/` - List leave balances
- `POST /api/leaves/balances/initialize_balances/` - Initialize balances for all employees
- `GET /api/leaves/holidays/` - List holidays

### Biometric Device Management
- `GET /api/biometric/devices/` - List devices
- `POST /api/biometric/devices/` - Add new device
- `POST /api/biometric/devices/{id}/test_connection/` - Test device connection
- `POST /api/biometric/devices/{id}/sync_users/` - Sync all users to device
- `POST /api/biometric/devices/{id}/sync_attendance/` - Sync attendance from device
- `GET /api/biometric/devices/{id}/get_users/` - Get users from device
- `GET /api/biometric/sync-logs/` - List sync logs
- `GET /api/biometric/sync-logs/statistics/` - Get sync statistics

## How It Works

### Employee Creation Flow
1. Create employee via API or Admin panel
2. System automatically assigns a biometric UID
3. Celery task pushes employee data to biometric device
4. Employee can now use fingerprint/card on device
5. Employee record marked as `biometric_synced=True`

### Attendance Tracking Flow
1. Employee punches in/out on biometric device
2. Celery Beat task runs every 5 minutes (configurable)
3. Task pulls new attendance records from device
4. Records matched with employees by biometric UID
5. Daily attendance summary automatically calculated
6. Work hours, overtime, and late status computed

### Leave Request Flow
1. Employee submits leave request via API
2. System validates against available leave balance
3. Manager approves/rejects via API
4. On approval, leave balance automatically deducted
5. Leave days marked in daily attendance as 'On Leave'

## Configuration

### Attendance Settings

Configure via Admin panel or API:
- **Standard Work Hours**: Default 8 hours
- **Shift Timings**: Start and end time
- **Grace Period**: Minutes allowed for late arrival
- **Overtime Threshold**: Hours after which overtime applies
- **Half Day Threshold**: Minimum hours for half day

### Celery Beat Schedule

Automatic tasks configured in `hrm_project/celery.py`:
- **Attendance Sync**: Every 5 minutes (300 seconds)

To change the interval, update `ATTENDANCE_SYNC_INTERVAL` in `.env`:
```env
ATTENDANCE_SYNC_INTERVAL=300  # seconds
```

## Docker Services

- **db**: PostgreSQL 15 database
- **web**: Django application server
- **celery**: Celery worker for background tasks
- **celery-beat**: Celery beat scheduler
- **redis**: Redis for Celery broker

## Useful Commands

### Docker Commands
```bash
# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f [service_name]

# Execute Django commands
docker-compose exec web python manage.py [command]

# Access Django shell
docker-compose exec web python manage.py shell

# Create migrations
docker-compose exec web python manage.py makemigrations

# Run migrations
docker-compose exec web python manage.py migrate
```

### Database Backup
```bash
# Backup database
docker-compose exec db pg_dump -U hrm_user hrm_db > backup.sql

# Restore database
docker-compose exec -T db psql -U hrm_user hrm_db < backup.sql
```

### Celery Tasks
```bash
# Monitor Celery worker
docker-compose logs -f celery

# Monitor Celery beat
docker-compose logs -f celery-beat
```

## Troubleshooting

### Biometric Device Connection Issues

1. **Check device IP and network connectivity**:
   ```bash
   ping 192.168.1.201
   ```

2. **Verify device settings in .env**:
   - Correct IP address
   - Correct port (usually 4370)
   - Correct password (usually 0)

3. **Test connection via API**:
   ```bash
   curl -X POST http://localhost:8000/api/biometric/devices/1/test_connection/
   ```

4. **Check sync logs**:
   ```bash
   curl http://localhost:8000/api/biometric/sync-logs/
   ```

### Employee Not Syncing to Device

1. Check employee has `biometric_user_id` assigned
2. Verify device is active and connected
3. Check Celery worker logs:
   ```bash
   docker-compose logs celery
   ```
4. Manually trigger sync:
   ```bash
   curl -X POST http://localhost:8000/api/employees/{id}/sync_to_biometric/
   ```

### Attendance Not Syncing

1. Verify Celery Beat is running:
   ```bash
   docker-compose ps celery-beat
   ```
2. Check last sync time in device record
3. Verify employees have matching `biometric_user_id`
4. Check sync logs for errors

## Development

### Project Structure
```
hrm/
├── hrm_project/          # Django project settings
│   ├── settings.py       # Main settings
│   ├── celery.py         # Celery configuration
│   └── urls.py           # URL routing
├── employees/            # Employee management app
├── attendance/           # Attendance tracking app
├── leaves/              # Leave management app
├── biometric/           # Biometric device integration
│   ├── services.py      # Device communication service
│   └── tasks.py         # Celery tasks
├── docker-compose.yml   # Docker services
├── Dockerfile           # Docker image
└── requirements.txt     # Python dependencies
```

### Adding New Features

1. Create new Django app if needed
2. Add models, serializers, views
3. Register in `INSTALLED_APPS`
4. Create migrations
5. Update API documentation

## Security Notes

⚠️ **Important for Production**:

1. Change `SECRET_KEY` in `.env`
2. Set `DEBUG=False`
3. Update `ALLOWED_HOSTS`
4. Use strong database passwords
5. Enable HTTPS
6. Implement proper authentication (JWT, OAuth)
7. Set up firewall rules for biometric device
8. Regular database backups
9. Monitor sync logs for suspicious activity

## License

This project is created for demonstration purposes.

## Support

For issues related to:
- **pyzk library**: https://github.com/fananimi/pyzk
- **Django**: https://docs.djangoproject.com/
- **ZKTeco devices**: Consult device manual

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

**Note**: Make sure your ZKTeco device is properly configured and accessible on your network before starting the application. The default IP address is set to `192.168.1.201` - update this in your `.env` file to match your device's actual IP address.
