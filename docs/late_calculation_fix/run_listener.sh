#!/bin/bash

# Configuration for Local Development (Same as run_local.sh)
export DB_NAME=hrm_db
export DB_USER=hrm_user
export DB_PASSWORD=hrm_password_2024
export LOCAL_DB_HOST=localhost
export DB_PORT=5432

export LOCAL_CELERY_BROKER_URL=redis://localhost:6379/0
export LOCAL_CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Biometric Device Config
export BIOMETRIC_DEVICE_IP=192.168.1.201
export BIOMETRIC_DEVICE_PORT=4370

echo "👂 Starting Biometric Real-time Listener..."

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the listener command
python3 manage.py listen_device
