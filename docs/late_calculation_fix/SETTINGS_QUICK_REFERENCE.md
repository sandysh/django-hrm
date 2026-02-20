# Quick Reference: SystemSettings

## Get Settings Instance
```python
from core.models import SystemSettings
settings = SystemSettings.get_settings()
```

## Core Settings (Typed Columns)
```python
# Office Hours
settings.office_start_time          # TimeField - e.g., 10:00:00
settings.office_end_time            # TimeField - e.g., 18:30:00
settings.late_threshold_minutes     # IntegerField - e.g., 15

# Work Hours & Thresholds
settings.standard_work_hours        # DecimalField - e.g., 8.00
settings.overtime_threshold_hours   # DecimalField - e.g., 8.00
settings.half_day_threshold_hours   # DecimalField - e.g., 4.00

# Break Settings
settings.lunch_break_duration       # IntegerField - e.g., 60 (minutes)

# Working Days
settings.working_days               # CharField - e.g., "1,2,3,4,5"

# Update and save
settings.office_start_time = '10:00:00'
settings.late_threshold_minutes = 15
settings.save()
```

## Additional Settings (JSON Field)
```python
# Get setting (with default)
value = settings.get_additional_setting('key', default_value)

# Set single setting
settings.set_additional_setting('key', value)
settings.save()

# Update multiple settings
settings.update_additional_settings({
    'email_enabled': True,
    'company_name': 'Acme Corp',
    'max_attempts': 5,
})
settings.save()
```

## Common Examples
```python
# Example 1: Check if email notifications are enabled
if settings.get_additional_setting('email_notifications', False):
    send_email()

# Example 2: Get company name
company = settings.get_additional_setting('company_name', 'My Company')

# Example 3: Add new feature flag
settings.set_additional_setting('new_feature_enabled', True)
settings.save()

# Example 4: Bulk update
settings.update_additional_settings({
    'timezone': 'Asia/Kathmandu',
    'date_format': 'YYYY-MM-DD',
    'currency': 'NPR',
})
settings.save()
```

## Migration Commands
```bash
# Apply all migrations
python manage.py migrate

# Recalculate attendance with new settings
python manage.py recalculate_late_status --all
```

## When to Use What

**Use Typed Columns** for:
- Critical settings (office hours, thresholds)
- Settings that need database validation
- Frequently accessed settings

**Use JSON Field** for:
- New features (no migration needed!)
- Optional/experimental settings
- Settings that might change

---
**See `HYBRID_SETTINGS_GUIDE.md` for complete documentation**
