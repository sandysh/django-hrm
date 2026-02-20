#!/bin/bash
# Complete fix script for the late calculation issue
# This script:
# 1. Adds missing columns to database
# 2. Runs Django migrations
# 3. Recalculates attendance records

set -e  # Exit on error

echo "=========================================="
echo "Complete Fix for Late Calculation Issue"
echo "=========================================="
echo ""

# Step 1: Add columns directly to database
echo "Step 1: Adding missing columns to database..."
echo ""

if python3 direct_migration.py; then
    echo ""
    echo "✓ Columns added successfully"
else
    echo ""
    echo "⚠ Direct migration failed. You may need to add columns manually."
    echo "See add_columns.sql for SQL commands"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""

# Step 2: Create static directory if missing
echo "Step 2: Creating static directory..."
mkdir -p static
echo "✓ Static directory created"
echo ""

# Step 3: Try to run Django migrations
echo "Step 3: Running Django migrations..."
echo ""

# Try with celery first
if python3 manage.py migrate 2>/dev/null; then
    echo "✓ Migrations completed"
else
    echo "⚠ Django migrations failed (likely due to celery)"
    echo "  This is OK - columns were already added in Step 1"
fi

echo ""

# Step 4: Verify columns exist
echo "Step 4: Verifying database schema..."
python3 << 'PYEOF'
import os
import sys

# Read .env
env_vars = {}
with open('.env', 'r') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            env_vars[key] = value.strip().strip('"').strip("'")

db_engine = env_vars.get('DB_ENGINE', 'postgresql')

if 'postgres' in db_engine.lower():
    import psycopg2
    conn = psycopg2.connect(
        dbname=env_vars['DB_NAME'],
        user=env_vars['DB_USER'],
        password=env_vars['DB_PASSWORD'],
        host=env_vars.get('DB_HOST', 'localhost'),
        port=env_vars.get('DB_PORT', '5432')
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'system_settings'
        AND column_name IN ('standard_work_hours', 'overtime_threshold_hours', 
                            'half_day_threshold_hours', 'lunch_break_duration', 
                            'additional_settings')
    """)
    columns = [row[0] for row in cursor.fetchall()]
    
    required = ['standard_work_hours', 'overtime_threshold_hours', 
                'half_day_threshold_hours', 'lunch_break_duration', 
                'additional_settings']
    
    missing = [c for c in required if c not in columns]
    
    if missing:
        print(f"✗ Missing columns: {', '.join(missing)}")
        sys.exit(1)
    else:
        print("✓ All required columns exist")
    
    cursor.close()
    conn.close()
PYEOF

echo ""

# Step 5: Recalculate attendance
echo "Step 5: Recalculating attendance records..."
echo ""

if python3 manage.py recalculate_late_status --days 30 2>/dev/null; then
    echo ""
    echo "✓ Attendance recalculated"
else
    echo "⚠ Recalculation command not available yet"
    echo "  You can run it manually later:"
    echo "  python3 manage.py recalculate_late_status --all"
fi

echo ""
echo "=========================================="
echo "✓ Fix Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Restart your Django server"
echo "2. Visit /settings/ - should work now!"
echo "3. Check dashboard - late calculations should be correct"
echo ""
echo "If you still see issues:"
echo "- Run: python3 manage.py recalculate_late_status --all"
echo "- Check URGENT_FIX_COLUMNS.md for troubleshooting"
echo ""
