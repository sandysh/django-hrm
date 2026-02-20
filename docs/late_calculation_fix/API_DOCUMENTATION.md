# HRM API Documentation

Complete API reference for the HRM application.

## Base URL
```
http://localhost:8000/api
```

## Authentication
Currently using Session Authentication. For production, consider implementing JWT or OAuth2.

---

## Employee Management

### List Employees
```http
GET /api/employees/
```

**Query Parameters:**
- `status` - Filter by status (AC, IN, SU, TE)
- `employment_type` - Filter by type (FT, PT, CT, IN)
- `department` - Filter by department
- `biometric_synced` - Filter by sync status (true/false)
- `search` - Search by employee_id, name, email
- `ordering` - Order by field (e.g., -created_at)

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "employee_id": "EMP001",
      "username": "john.doe",
      "full_name": "John Doe",
      "email": "john.doe@example.com",
      "department": "Engineering",
      "designation": "Software Developer",
      "status": "AC",
      "biometric_synced": true
    }
  ]
}
```

### Create Employee
```http
POST /api/employees/
```

**Request Body:**
```json
{
  "employee_id": "EMP002",
  "username": "jane.smith",
  "email": "jane.smith@example.com",
  "password": "secure_password",
  "first_name": "Jane",
  "last_name": "Smith",
  "phone_number": "+9779841234567",
  "date_of_birth": "1990-05-15",
  "gender": "F",
  "address": "Kathmandu, Nepal",
  "department": "HR",
  "designation": "HR Manager",
  "employment_type": "FT",
  "date_joined_company": "2024-01-01",
  "status": "AC"
}
```

**Response:** 201 Created
```json
{
  "id": 2,
  "employee_id": "EMP002",
  "username": "jane.smith",
  "email": "jane.smith@example.com",
  "full_name": "Jane Smith",
  "biometric_user_id": 2,
  "biometric_synced": false,
  "created_at": "2024-12-18T10:30:00Z"
}
```

### Get Employee Details
```http
GET /api/employees/{id}/
```

### Update Employee
```http
PUT /api/employees/{id}/
PATCH /api/employees/{id}/
```

### Delete Employee
```http
DELETE /api/employees/{id}/
```

### Sync Employee to Biometric Device
```http
POST /api/employees/{id}/sync_to_biometric/
```

**Response:**
```json
{
  "message": "Biometric sync task initiated",
  "task_id": "abc123-def456",
  "employee_id": "EMP001"
}
```

### Get Employee Statistics
```http
GET /api/employees/statistics/
```

**Response:**
```json
{
  "total_employees": 50,
  "active_employees": 45,
  "inactive_employees": 5,
  "biometric_synced": 42,
  "biometric_not_synced": 8,
  "by_department": {
    "Engineering": 20,
    "HR": 5,
    "Sales": 15,
    "Finance": 10
  }
}
```

---

## Attendance Management

### List Attendance Records
```http
GET /api/attendance/records/
```

**Query Parameters:**
- `employee` - Filter by employee ID
- `punch_type` - Filter by type (IN, OUT, BREAK_OUT, BREAK_IN)
- `is_manual` - Filter manual records (true/false)
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "employee": 1,
      "employee_details": {
        "employee_id": "EMP001",
        "full_name": "John Doe"
      },
      "punch_time": "2024-12-18T09:00:00Z",
      "punch_type": "IN",
      "biometric_user_id": 1,
      "is_manual": false,
      "synced_at": "2024-12-18T09:05:00Z"
    }
  ]
}
```

### Create Manual Attendance Record
```http
POST /api/attendance/records/
```

**Request Body:**
```json
{
  "employee": 1,
  "punch_time": "2024-12-18T09:00:00Z",
  "punch_type": "IN",
  "is_manual": true,
  "notes": "Manual entry - device was offline"
}
```

### List Daily Attendance
```http
GET /api/attendance/daily/
```

**Query Parameters:**
- `employee` - Filter by employee ID
- `status` - Filter by status (PR, AB, HL, LT, LV, WO, HO)
- `is_late` - Filter late arrivals (true/false)
- `is_overtime` - Filter overtime (true/false)
- `start_date` - From date
- `end_date` - To date

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "employee": 1,
      "employee_details": {
        "employee_id": "EMP001",
        "full_name": "John Doe"
      },
      "date": "2024-12-18",
      "status": "PR",
      "check_in_time": "09:00:00",
      "check_out_time": "17:30:00",
      "total_hours": 8.50,
      "is_late": false,
      "is_overtime": true,
      "overtime_hours": 0.50
    }
  ]
}
```

### Get Attendance Summary
```http
GET /api/attendance/daily/summary/?start_date=2024-01-01&end_date=2024-12-31
```

**Required Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)
- `employee_id` - (Optional) Filter by employee

**Response:**
```json
[
  {
    "employee_id": "EMP001",
    "employee_name": "John Doe",
    "total_days": 250,
    "present_days": 230,
    "absent_days": 10,
    "half_days": 5,
    "late_days": 15,
    "leave_days": 10,
    "total_hours": 1840.00,
    "average_hours": 8.00,
    "overtime_hours": 25.50
  }
]
```

### Sync Attendance from Device
```http
POST /api/attendance/daily/sync_from_device/
```

**Response:**
```json
{
  "message": "Attendance sync task initiated",
  "task_id": "xyz789-abc123"
}
```

### Get Attendance Settings
```http
GET /api/attendance/settings/
```

### Update Attendance Settings
```http
PUT /api/attendance/settings/1/
```

**Request Body:**
```json
{
  "standard_work_hours": 8.00,
  "grace_period_minutes": 15,
  "shift_start_time": "09:00:00",
  "shift_end_time": "17:00:00",
  "lunch_break_duration": 60,
  "overtime_threshold_hours": 8.00,
  "half_day_threshold_hours": 4.00
}
```

---

## Leave Management

### List Leave Types
```http
GET /api/leaves/types/
```

**Response:**
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "name": "Annual Leave",
      "code": "AL",
      "description": "Annual vacation leave",
      "default_days": 15,
      "is_paid": true,
      "requires_approval": true,
      "is_active": true
    }
  ]
}
```

### Create Leave Type
```http
POST /api/leaves/types/
```

### List Leave Requests
```http
GET /api/leaves/requests/
```

**Query Parameters:**
- `employee` - Filter by employee
- `leave_type` - Filter by leave type
- `status` - Filter by status (PE, AP, RJ, CA)
- `start_date` - From date
- `end_date` - To date

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": 1,
      "employee": 1,
      "employee_details": {
        "employee_id": "EMP001",
        "full_name": "John Doe"
      },
      "leave_type": 1,
      "leave_type_details": {
        "name": "Annual Leave",
        "code": "AL"
      },
      "start_date": "2024-12-20",
      "end_date": "2024-12-22",
      "total_days": 3,
      "reason": "Family vacation",
      "status": "PE",
      "created_at": "2024-12-18T10:00:00Z"
    }
  ]
}
```

### Submit Leave Request
```http
POST /api/leaves/requests/
```

**Request Body:**
```json
{
  "employee": 1,
  "leave_type": 1,
  "start_date": "2024-12-20",
  "end_date": "2024-12-22",
  "reason": "Family vacation",
  "attachment": null
}
```

### Approve Leave Request
```http
POST /api/leaves/requests/{id}/approve/
```

**Request Body:**
```json
{
  "notes": "Approved. Enjoy your vacation!"
}
```

### Reject Leave Request
```http
POST /api/leaves/requests/{id}/reject/
```

**Request Body:**
```json
{
  "notes": "Cannot approve due to project deadline"
}
```

### Cancel Leave Request
```http
POST /api/leaves/requests/{id}/cancel/
```

### List Leave Balances
```http
GET /api/leaves/balances/
```

**Query Parameters:**
- `employee` - Filter by employee
- `leave_type` - Filter by leave type
- `year` - Filter by year

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": 1,
      "employee": 1,
      "employee_details": {
        "employee_id": "EMP001",
        "full_name": "John Doe"
      },
      "leave_type": 1,
      "leave_type_details": {
        "name": "Annual Leave",
        "code": "AL"
      },
      "year": 2024,
      "allocated": 15.00,
      "used": 5.00,
      "balance": 10.00
    }
  ]
}
```

### Initialize Leave Balances
```http
POST /api/leaves/balances/initialize_balances/
```

**Request Body:**
```json
{
  "year": 2024
}
```

**Response:**
```json
{
  "message": "Initialized 120 leave balances for year 2024"
}
```

### List Holidays
```http
GET /api/leaves/holidays/
```

**Query Parameters:**
- `year` - Filter by year
- `is_optional` - Filter optional holidays

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "New Year",
      "date": "2024-01-01",
      "description": "New Year's Day",
      "is_optional": false
    }
  ]
}
```

### Create Holiday
```http
POST /api/leaves/holidays/
```

**Request Body:**
```json
{
  "name": "Independence Day",
  "date": "2024-08-15",
  "description": "National Independence Day",
  "is_optional": false
}
```

---

## Biometric Device Management

### List Devices
```http
GET /api/biometric/devices/
```

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "name": "Main Office Biometric Device",
      "ip_address": "192.168.1.201",
      "port": 4370,
      "is_active": true,
      "last_connection_status": true,
      "last_sync_time": "2024-12-18T10:00:00Z",
      "firmware_version": "Ver 6.60 Apr 28 2017",
      "serial_number": "BNVR123456789"
    }
  ]
}
```

### Test Device Connection
```http
POST /api/biometric/devices/{id}/test_connection/
```

**Response:**
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

### Sync All Users to Device
```http
POST /api/biometric/devices/{id}/sync_users/
```

### Sync Attendance from Device
```http
POST /api/biometric/devices/{id}/sync_attendance/
```

### Get Users from Device
```http
GET /api/biometric/devices/{id}/get_users/
```

**Response:**
```json
{
  "total_users": 50,
  "users": [
    {
      "uid": 1,
      "name": "John Doe",
      "privilege": 0,
      "user_id": "EMP001",
      "group_id": ""
    }
  ]
}
```

### List Sync Logs
```http
GET /api/biometric/sync-logs/
```

**Query Parameters:**
- `sync_type` - Filter by type (USER_PUSH, USER_PULL, ATTENDANCE_PULL, DEVICE_INFO)
- `status` - Filter by status (SU, FA, PA)
- `device` - Filter by device ID
- `start_date` - From date
- `end_date` - To date

**Response:**
```json
{
  "count": 100,
  "results": [
    {
      "id": 1,
      "sync_type": "ATTENDANCE_PULL",
      "status": "SU",
      "records_processed": 50,
      "records_success": 48,
      "records_failed": 2,
      "started_at": "2024-12-18T10:00:00Z",
      "completed_at": "2024-12-18T10:00:15Z",
      "duration_seconds": 15.23,
      "error_message": ""
    }
  ]
}
```

### Get Sync Statistics
```http
GET /api/biometric/sync-logs/statistics/
```

**Response:**
```json
{
  "total_syncs": 500,
  "successful_syncs": 480,
  "failed_syncs": 15,
  "partial_syncs": 5,
  "avg_duration": 12.45,
  "total_records_processed": 25000,
  "total_records_success": 24500,
  "total_records_failed": 500
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid data provided",
  "details": {
    "email": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "An unexpected error occurred",
  "message": "Error details..."
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider implementing rate limiting using Django REST Framework throttling.

## Pagination

All list endpoints support pagination:
- Default page size: 50 items
- Use `?page=2` for next page
- Response includes `count`, `next`, and `previous` fields

## Filtering and Searching

Most list endpoints support:
- **Filtering**: Use query parameters (e.g., `?status=AC`)
- **Searching**: Use `?search=keyword`
- **Ordering**: Use `?ordering=-created_at` (prefix with `-` for descending)

---

## Postman Collection

Import the API into Postman for easy testing:

1. Create new collection
2. Set base URL variable: `{{base_url}}` = `http://localhost:8000/api`
3. Add requests from this documentation
4. Configure authentication

---

**Last Updated**: December 18, 2024
