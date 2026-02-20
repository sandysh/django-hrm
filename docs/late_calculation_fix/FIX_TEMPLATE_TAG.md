# Fix: Template Tag Not Registered

## Error
```
'attendance_tags' is not a registered tag library
```

## Cause
Django hasn't loaded the new template tag library yet.

## Solution

### Step 1: Restart Django Server

**Stop your current server:**
- Press `Ctrl+C` in the terminal where Django is running

**Start it again:**
```bash
cd /Users/sandy/projects/python/hrm
python3 manage.py runserver
```

### Step 2: Clear Python Cache (if restart doesn't work)

```bash
cd /Users/sandy/projects/python/hrm

# Remove Python cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete

# Restart server
python3 manage.py runserver
```

### Step 3: Verify Template Tag Structure

The files should exist:
```
attendance/
├── templatetags/
│   ├── __init__.py          ✅ (empty file)
│   └── attendance_tags.py   ✅ (template tag code)
```

Check:
```bash
ls -la attendance/templatetags/
# Should show both files
```

### Step 4: If Still Not Working

Django might have celery import issues. Try this workaround:

**Temporarily disable celery:**

Edit `hrm_project/__init__.py`:
```python
# Comment out these lines:
# from .celery import app as celery_app
# __all__ = ('celery_app',)
```

Then restart server.

## Quick Fix Script

```bash
cd /Users/sandy/projects/python/hrm

# Clean cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Verify files exist
ls -la attendance/templatetags/

# Restart server (stop current one first with Ctrl+C)
python3 manage.py runserver
```

## After Restart

The template tag should work:
```html
{% load attendance_tags %}
{% is_late attendance.check_in_time attendance.date as late_status %}
```

---

**Most likely you just need to restart the Django server!** 🔄
