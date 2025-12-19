#!/bin/bash

# Configuration for Local Development
export DB_NAME=hrm_db
export DB_USER=hrm_user
export DB_PASSWORD=hrm_password_2024
export LOCAL_DB_HOST=localhost
export DB_PORT=5432

export LOCAL_CELERY_BROKER_URL=redis://localhost:6379/0
export LOCAL_CELERY_RESULT_BACKEND=redis://localhost:6379/0

export BIOMETRIC_DEVICE_IP=192.168.1.201
export BIOMETRIC_DEVICE_PORT=4370

echo "🔧 Creating migrations for SystemSettings..."

# Activate venv if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Create migrations
python3 manage.py makemigrations core

# Run migrations
python3 manage.py migrate

echo "✅ Migrations complete!"
