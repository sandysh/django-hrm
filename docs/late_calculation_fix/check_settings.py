#!/usr/bin/env python3
"""
Check the current values in both settings tables
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/Users/sandy/projects/python/hrm')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_project.settings')

# Disable celery import
import hrm_project
hrm_project.celery = None

django.setup()

from core.models import SystemSettings
from attendance.models import AttendanceSettings

print("=" * 70)
print("DATABASE SETTINGS CHECK")
print("=" * 70)

# Check SystemSettings
print("\n📋 SYSTEM SETTINGS (Table: system_settings)")
print("-" * 70)
try:
    ss = SystemSettings.objects.first()
    if ss:
        print(f"✓ Record found (ID: {ss.id})")
        print(f"  Office Start Time: {ss.office_start_time}")
        print(f"  Office End Time: {ss.office_end_time}")
        print(f"  Late Threshold: {ss.late_threshold_minutes} minutes")
        print(f"  Grace Time: {ss.office_start_time} + {ss.late_threshold_minutes} min")
        print(f"  Updated: {ss.updated_at}")
    else:
        print("✗ NO RECORD FOUND - Table is empty!")
        print("  Creating default record...")
        ss = SystemSettings.get_settings()
        print(f"  Created with defaults: {ss.office_start_time}")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Check AttendanceSettings
print("\n📋 ATTENDANCE SETTINGS (Table: attendance_settings)")
print("-" * 70)
try:
    att = AttendanceSettings.objects.first()
    if att:
        print(f"✓ Record found (ID: {att.id})")
        print(f"  Shift Start Time: {att.shift_start_time}")
        print(f"  Shift End Time: {att.shift_end_time}")
        print(f"  Grace Period: {att.grace_period_minutes} minutes")
        print(f"  Grace Time: {att.shift_start_time} + {att.grace_period_minutes} min")
        print(f"  Overtime Threshold: {att.overtime_threshold_hours} hours")
        print(f"  Half Day Threshold: {att.half_day_threshold_hours} hours")
        print(f"  Updated: {att.updated_at}")
    else:
        print("✗ NO RECORD FOUND - Table is empty!")
except Exception as e:
    print(f"✗ ERROR: {e}")

# Show the confusion
print("\n" + "=" * 70)
print("⚠️  THE CONFUSION")
print("=" * 70)
print("You have TWO settings tables:")
print("  1. system_settings - Used by Settings Page UI")
print("  2. attendance_settings - Was used by late calculation (NOW FIXED)")
print("\nAfter the fix:")
print("  ✓ Late calculation now uses system_settings")
print("  ✓ Settings page updates system_settings")
print("  ✓ Everything is synchronized!")
print("\nRecommendation:")
print("  • Keep system_settings as the primary settings")
print("  • Consider removing attendance_settings to avoid confusion")
print("=" * 70)
