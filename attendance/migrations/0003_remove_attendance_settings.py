# Migration to remove AttendanceSettings model and table

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('attendance', '0002_initial'),  # Updated to depend on existing 0002_initial
        ('core', '0003_migrate_attendance_settings_data'),  # Ensure data is migrated first
    ]

    operations = [
        migrations.DeleteModel(
            name='AttendanceSettings',
        ),
    ]
