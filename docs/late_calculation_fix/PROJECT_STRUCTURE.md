# Project Structure

```
hrm/
├── docker-compose.yml          # Docker services configuration
├── Dockerfile                  # Docker image definition
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create from .env.example)
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── Makefile                   # Convenient make commands
├── quickstart.sh              # Quick start script
├── manage.py                  # Django management script
├── README.md                  # Main documentation
├── SETUP_GUIDE.md            # Detailed setup guide
├── API_DOCUMENTATION.md      # API reference
│
├── hrm_project/              # Django project configuration
│   ├── __init__.py
│   ├── settings.py           # Django settings
│   ├── urls.py               # Main URL routing
│   ├── wsgi.py               # WSGI configuration
│   ├── asgi.py               # ASGI configuration
│   └── celery.py             # Celery configuration
│
├── employees/                # Employee management app
│   ├── __init__.py
│   ├── models.py             # Employee model (extends User)
│   ├── admin.py              # Admin interface
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   ├── apps.py               # App configuration
│   ├── signals.py            # Django signals
│   └── management/           # Management commands
│       └── commands/
│           └── init_hrm.py   # Initialize HRM system
│
├── attendance/               # Attendance tracking app
│   ├── __init__.py
│   ├── models.py             # Attendance models
│   │   ├── AttendanceRecord  # Raw punch records
│   │   ├── DailyAttendance   # Daily summaries
│   │   └── AttendanceSettings # Configuration
│   ├── admin.py              # Admin interface
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   └── apps.py               # App configuration
│
├── leaves/                   # Leave management app
│   ├── __init__.py
│   ├── models.py             # Leave models
│   │   ├── LeaveType         # Leave type definitions
│   │   ├── LeaveRequest      # Leave requests
│   │   ├── Holiday           # Public holidays
│   │   └── LeaveBalance      # Employee leave balances
│   ├── admin.py              # Admin interface
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   └── apps.py               # App configuration
│
├── biometric/                # Biometric device integration
│   ├── __init__.py
│   ├── models.py             # Biometric models
│   │   ├── BiometricDevice   # Device configuration
│   │   └── SyncLog           # Sync activity logs
│   ├── services.py           # Device communication service
│   │   └── BiometricDeviceService # pyzk wrapper
│   ├── tasks.py              # Celery tasks
│   │   ├── sync_employee_to_device
│   │   ├── sync_attendance_from_device
│   │   ├── sync_all_employees_to_device
│   │   └── fetch_device_info
│   ├── admin.py              # Admin interface
│   ├── serializers.py        # DRF serializers
│   ├── views.py              # API views
│   ├── urls.py               # URL routing
│   └── apps.py               # App configuration
│
├── static/                   # Static files (CSS, JS, images)
├── staticfiles/              # Collected static files (generated)
├── media/                    # User uploaded files
└── templates/                # HTML templates (if needed)
```

## Key Components

### Django Apps

1. **employees** - Employee/User management
   - Custom User model extending AbstractUser
   - Employee profiles with biometric integration
   - Department and designation management
   - Leave balance tracking

2. **attendance** - Attendance tracking
   - Raw attendance records from biometric device
   - Daily attendance summaries
   - Work hours calculation
   - Late/overtime tracking
   - Configurable attendance policies

3. **leaves** - Leave management
   - Multiple leave types
   - Leave request workflow
   - Approval/rejection system
   - Leave balance management
   - Holiday calendar

4. **biometric** - Device integration
   - ZKTeco device connectivity
   - User synchronization
   - Attendance data pull
   - Sync logging and monitoring

### Background Tasks (Celery)

- **Periodic Tasks** (Celery Beat):
  - Attendance sync every 5 minutes
  
- **On-Demand Tasks**:
  - Employee sync to device
  - Manual attendance sync
  - Device info fetch

### Database Schema

**Key Tables:**
- `employees` - Employee/user data
- `attendance_records` - Raw punch records
- `daily_attendance` - Daily summaries
- `leave_requests` - Leave applications
- `leave_balances` - Employee leave balances
- `biometric_devices` - Device configurations
- `sync_logs` - Synchronization logs

### API Endpoints

All endpoints are RESTful and follow standard conventions:
- `GET /api/{resource}/` - List
- `POST /api/{resource}/` - Create
- `GET /api/{resource}/{id}/` - Retrieve
- `PUT /api/{resource}/{id}/` - Update
- `PATCH /api/{resource}/{id}/` - Partial update
- `DELETE /api/{resource}/{id}/` - Delete

Custom actions use POST with descriptive names:
- `POST /api/employees/{id}/sync_to_biometric/`
- `POST /api/leaves/requests/{id}/approve/`

## Technology Stack

### Backend
- **Django 4.2.8** - Web framework
- **Django REST Framework** - API framework
- **PostgreSQL 15** - Database
- **Celery** - Task queue
- **Redis** - Message broker
- **pyzk 0.9.1** - Biometric device library

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

### Python Libraries
- `psycopg2-binary` - PostgreSQL adapter
- `python-decouple` - Environment variable management
- `django-cors-headers` - CORS handling
- `django-filter` - Advanced filtering
- `Pillow` - Image processing

## Data Flow

### Employee Creation Flow
```
User creates employee
    ↓
Employee model saved
    ↓
Celery task triggered
    ↓
BiometricDeviceService connects to device
    ↓
Employee pushed to device
    ↓
Employee marked as synced
```

### Attendance Sync Flow
```
Celery Beat triggers (every 5 min)
    ↓
BiometricDeviceService connects
    ↓
Fetch attendance records
    ↓
Match with employees by UID
    ↓
Create AttendanceRecord entries
    ↓
Update DailyAttendance summaries
    ↓
Calculate work hours, overtime, etc.
```

### Leave Request Flow
```
Employee submits request
    ↓
Validate against balance
    ↓
Manager approves/rejects
    ↓
Update leave balance
    ↓
Mark days in daily attendance
```

## Configuration Files

- **docker-compose.yml** - Services definition
- **Dockerfile** - Image build instructions
- **.env** - Environment variables
- **requirements.txt** - Python dependencies
- **Makefile** - Command shortcuts
- **settings.py** - Django configuration

## Development Workflow

1. Make code changes
2. Rebuild if needed: `make build`
3. Restart services: `make restart`
4. Run migrations: `make migrate`
5. Check logs: `make logs`
6. Test changes

## Deployment Considerations

- Use environment variables for all secrets
- Set DEBUG=False in production
- Use proper SECRET_KEY
- Configure ALLOWED_HOSTS
- Set up HTTPS/SSL
- Use production-grade WSGI server (gunicorn)
- Set up monitoring and logging
- Configure database backups
- Use Redis persistence
- Set up firewall rules
