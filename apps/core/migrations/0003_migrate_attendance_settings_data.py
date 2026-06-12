# Data migration to copy settings from AttendanceSettings to SystemSettings

from django.db import migrations


def migrate_attendance_settings(apps, schema_editor):
    """Copy data from AttendanceSettings to SystemSettings if it exists."""
    SystemSettings = apps.get_model('core', 'SystemSettings')
    
    # Try to get AttendanceSettings - it might not exist if table was already dropped
    try:
        AttendanceSettings = apps.get_model('attendance', 'AttendanceSettings')
        att_settings = AttendanceSettings.objects.first()
        
        if att_settings:
            # Get or create SystemSettings
            sys_settings, created = SystemSettings.objects.get_or_create(pk=1)
            
            # Copy the fields
            sys_settings.standard_work_hours = att_settings.standard_work_hours
            sys_settings.overtime_threshold_hours = att_settings.overtime_threshold_hours
            sys_settings.half_day_threshold_hours = att_settings.half_day_threshold_hours
            sys_settings.lunch_break_duration = att_settings.lunch_break_duration
            
            # Also update office times if they match shift times
            if hasattr(att_settings, 'shift_start_time'):
                sys_settings.office_start_time = att_settings.shift_start_time
            if hasattr(att_settings, 'shift_end_time'):
                sys_settings.office_end_time = att_settings.shift_end_time
            if hasattr(att_settings, 'grace_period_minutes'):
                sys_settings.late_threshold_minutes = att_settings.grace_period_minutes
            
            sys_settings.save()
            print(f"✓ Migrated settings from AttendanceSettings to SystemSettings")
        else:
            print("  No AttendanceSettings found to migrate")
    except Exception as e:
        print(f"  Note: Could not migrate AttendanceSettings (may not exist): {e}")
        # Ensure SystemSettings exists with defaults
        SystemSettings.objects.get_or_create(pk=1)


def reverse_migration(apps, schema_editor):
    """Reverse migration - no action needed."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_add_attendance_fields_to_system_settings'),
        ('attendance', '0001_initial'),  # Ensure attendance app migrations have run
    ]

    operations = [
        migrations.RunPython(migrate_attendance_settings, reverse_migration),
    ]
