#!/bin/bash

# Configuration for Local Development (Mac Host)
# Connecting to Docker services (Postgres & Redis) exposed on localhost ports

export DB_NAME=hrm_db
export DB_USER=hrm_user
export DB_PASSWORD=hrm_password_2024
export LOCAL_DB_HOST=localhost
export DB_PORT=5432

export LOCAL_CELERY_BROKER_URL=redis://localhost:6379/0
export LOCAL_CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Biometric Device Config (Already matches .env but good to be explicit)
export BIOMETRIC_DEVICE_IP=192.168.1.201
export BIOMETRIC_DEVICE_PORT=4370

echo "🚀 Starting HRM Server Locally..."
echo "🔌 Connecting to Database at localhost:5432"
echo "📶 Biometric Device: $BIOMETRIC_DEVICE_IP:$BIOMETRIC_DEVICE_PORT"

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the server
python3 manage.py runserver 0.0.0.0:8000
