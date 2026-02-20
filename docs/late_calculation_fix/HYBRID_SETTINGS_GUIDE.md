# SystemSettings: Hybrid Approach Guide

## Overview

The `SystemSettings` model uses a **hybrid approach** combining:
1. **Typed columns** for core, frequently-used settings (type-safe, validated)
2. **JSON field** for flexible additional settings (no migrations needed)

This gives you the best of both worlds: type safety for critical settings AND flexibility for future additions.

## Core Settings (Typed Columns)

These settings use dedicated database columns with proper types and validation:

```python
from core.models import SystemSettings

settings = SystemSettings.get_settings()

# Office Hours
settings.office_start_time  # TimeField
settings.office_end_time    # TimeField
settings.late_threshold_minutes  # IntegerField

# Working Hours & Thresholds
settings.standard_work_hours  # DecimalField
settings.overtime_threshold_hours  # DecimalField
settings.half_day_threshold_hours  # DecimalField

# Break Settings
settings.lunch_break_duration  # IntegerField

# Working Days
settings.working_days  # CharField (comma-separated)
```

### When to Use Typed Columns
- ✅ Settings that need database-level validation
- ✅ Settings used frequently in code
- ✅ Settings with specific types (time, decimal, etc.)
- ✅ Critical settings that should never be invalid

## Additional Settings (JSON Field)

For new settings that don't need dedicated columns, use the `additional_settings` JSON field:

### Basic Usage

```python
from core.models import SystemSettings

settings = SystemSettings.get_settings()

# Get a setting (with default)
email_enabled = settings.get_additional_setting('email_notifications', True)
max_attempts = settings.get_additional_setting('max_login_attempts', 3)
company_name = settings.get_additional_setting('company_name', 'My Company')

# Set a single setting
settings.set_additional_setting('email_notifications', True)
settings.set_additional_setting('company_name', 'Acme Corporation')
settings.save()  # Don't forget to save!

# Update multiple settings at once
settings.update_additional_settings({
    'email_notifications': True,
    'sms_notifications': False,
    'max_login_attempts': 5,
    'company_name': 'Acme Corp',
    'company_logo_url': '/media/logo.png',
    'timezone': 'Asia/Kathmandu',
    'date_format': 'YYYY-MM-DD',
})
settings.save()
```

### Example: Adding New Settings

**Scenario**: You want to add email notification settings

```python
# No migration needed! Just use the additional_settings field

settings = SystemSettings.get_settings()

# Add email settings
settings.update_additional_settings({
    'email_notifications_enabled': True,
    'email_from_address': 'noreply@company.com',
    'email_smtp_host': 'smtp.gmail.com',
    'email_smtp_port': 587,
    'notify_on_late_arrival': True,
    'notify_on_leave_request': True,
})
settings.save()

# Later, retrieve them
if settings.get_additional_setting('email_notifications_enabled', False):
    from_email = settings.get_additional_setting('email_from_address')
    smtp_host = settings.get_additional_setting('email_smtp_host')
    # Send email...
```

### When to Use Additional Settings
- ✅ New features that need configuration
- ✅ Settings that might change frequently
- ✅ Optional/experimental settings
- ✅ Settings that don't need database validation
- ✅ When you want to avoid migrations

## Data Types in JSON Field

The JSON field can store various Python types:

```python
settings.update_additional_settings({
    # Strings
    'company_name': 'Acme Corp',
    
    # Numbers
    'max_login_attempts': 5,
    'session_timeout_minutes': 30.5,
    
    # Booleans
    'email_enabled': True,
    'debug_mode': False,
    
    # Lists
    'allowed_ips': ['192.168.1.1', '10.0.0.1'],
    'notification_channels': ['email', 'sms', 'push'],
    
    # Dictionaries (nested)
    'email_config': {
        'host': 'smtp.gmail.com',
        'port': 587,
        'use_tls': True,
    },
    
    # Dates/Times (store as strings)
    'maintenance_window': '2025-12-25T00:00:00',
})
```

## Migration Path

### Adding a New Setting (No Migration)

```python
# Just add it to additional_settings
settings = SystemSettings.get_settings()
settings.set_additional_setting('new_feature_enabled', True)
settings.save()
```

### Promoting to Typed Column (If Needed Later)

If a setting becomes critical and needs validation:

1. **Create a migration** to add the typed column
2. **Migrate data** from JSON to column
3. **Update code** to use the typed field
4. **Remove** from additional_settings

Example:

```python
# Step 1: Create migration
# core/migrations/0004_add_company_name.py
operations = [
    migrations.AddField(
        model_name='systemsettings',
        name='company_name',
        field=models.CharField(max_length=200, default='My Company'),
    ),
]

# Step 2: Data migration
def migrate_company_name(apps, schema_editor):
    SystemSettings = apps.get_model('core', 'SystemSettings')
    settings = SystemSettings.objects.first()
    if settings and 'company_name' in settings.additional_settings:
        settings.company_name = settings.additional_settings['company_name']
        del settings.additional_settings['company_name']
        settings.save()

# Step 3: Update code
# Old: settings.get_additional_setting('company_name')
# New: settings.company_name
```

## Best Practices

### 1. Use Consistent Naming
```python
# Good
settings.set_additional_setting('email_notifications_enabled', True)
settings.set_additional_setting('sms_notifications_enabled', False)

# Bad (inconsistent)
settings.set_additional_setting('emailNotifications', True)
settings.set_additional_setting('SMS_enabled', False)
```

### 2. Always Provide Defaults
```python
# Good - won't break if setting doesn't exist
enabled = settings.get_additional_setting('feature_enabled', False)

# Bad - could return None unexpectedly
enabled = settings.get_additional_setting('feature_enabled')
```

### 3. Document Your Settings
```python
# Create a constants file for additional settings
# core/settings_keys.py

# Email Settings
EMAIL_NOTIFICATIONS_ENABLED = 'email_notifications_enabled'
EMAIL_FROM_ADDRESS = 'email_from_address'
EMAIL_SMTP_HOST = 'email_smtp_host'

# Usage
from core.settings_keys import EMAIL_NOTIFICATIONS_ENABLED
enabled = settings.get_additional_setting(EMAIL_NOTIFICATIONS_ENABLED, False)
```

### 4. Type Conversion
```python
# JSON stores everything as JSON types
# Be explicit about type conversion when needed

# For booleans
enabled = bool(settings.get_additional_setting('feature_enabled', False))

# For integers
max_attempts = int(settings.get_additional_setting('max_attempts', 3))

# For decimals
from decimal import Decimal
threshold = Decimal(str(settings.get_additional_setting('threshold', 0.5)))
```

## Example: Settings Management View

```python
# views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from core.models import SystemSettings

def manage_additional_settings(request):
    settings = SystemSettings.get_settings()
    
    if request.method == 'POST':
        # Update additional settings from form
        settings.update_additional_settings({
            'email_notifications': request.POST.get('email_notifications') == 'on',
            'company_name': request.POST.get('company_name', ''),
            'max_login_attempts': int(request.POST.get('max_login_attempts', 3)),
        })
        settings.save()
        messages.success(request, 'Settings updated successfully!')
        return redirect('settings')
    
    context = {
        'settings': settings,
        'email_notifications': settings.get_additional_setting('email_notifications', True),
        'company_name': settings.get_additional_setting('company_name', 'My Company'),
        'max_login_attempts': settings.get_additional_setting('max_login_attempts', 3),
    }
    return render(request, 'settings.html', context)
```

## Advantages of This Approach

| Aspect | Typed Columns | JSON Field |
|--------|--------------|------------|
| **Type Safety** | ✅ Database enforced | ⚠️ Application level |
| **Validation** | ✅ Automatic | ⚠️ Manual |
| **Migrations** | ❌ Required | ✅ Not needed |
| **Flexibility** | ❌ Fixed schema | ✅ Dynamic |
| **Performance** | ✅ Indexed, fast | ⚠️ Slower queries |
| **IDE Support** | ✅ Autocomplete | ❌ No autocomplete |
| **Best For** | Core settings | Optional features |

## Summary

✅ **Use typed columns** for:
- Office hours, thresholds, core business logic
- Settings that need validation
- Frequently accessed settings

✅ **Use additional_settings JSON** for:
- New features and experiments
- Optional configurations
- Settings that change often
- Avoiding migrations

This hybrid approach gives you **flexibility without sacrificing safety** for critical settings! 🚀
