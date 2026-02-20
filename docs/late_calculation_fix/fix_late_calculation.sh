#!/bin/bash
# Script to apply all changes and fix the late calculation issue

echo "=========================================="
echo "Fixing Late Calculation Issue"
echo "=========================================="
echo ""

# Step 1: Run migrations
echo "Step 1: Running migrations..."
python3 manage.py migrate core 0002_add_attendance_fields_to_system_settings
python3 manage.py migrate core 0003_migrate_attendance_settings_data
python3 manage.py migrate attendance 0002_remove_attendance_settings

echo ""
echo "✓ Migrations completed"
echo ""

# Step 2: Show current settings
echo "Step 2: Current SystemSettings:"
python3 manage.py shell << 'PYEOF'
from core.models import SystemSettings
settings = SystemSettings.get_settings()
print(f"  Office Start Time: {settings.office_start_time}")
print(f"  Late Threshold: {settings.late_threshold_minutes} minutes")
print(f"  Grace Time: {settings.office_start_time} + {settings.late_threshold_minutes} min")
PYEOF

echo ""

# Step 3: Recalculate attendance
echo "Step 3: Recalculating attendance records..."
echo "  This will fix all existing records to use the correct settings"
echo ""
python3 manage.py recalculate_late_status --days 30

echo ""
echo "=========================================="
echo "✓ All Done!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Check the dashboard - users punching in at 10:00 AM should NOT be late"
echo "2. Check attendance reports - late status should be correct"
echo "3. If you want to recalculate ALL records (not just last 30 days):"
echo "   python3 manage.py recalculate_late_status --all"
echo ""
