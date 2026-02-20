# URGENT FIX: Column Does Not Exist Error

## Error
```
ProgrammingError at /settings/
column system_settings.standard_work_hours does not exist
```

## Cause
The model code expects new columns, but they haven't been added to the database yet.

## Solution: Add Columns to Database

You have **3 options** to fix this:

---

## Option 1: Direct Python Script (Recommended - Easiest)

Run the direct migration script:

```bash
cd /Users/sandy/projects/python/hrm
python3 direct_migration.py
```

This will:
- Connect to your database
- Add all missing columns
- Verify they were added

**Then restart your Django server.**

---

## Option 2: Manual SQL (If Option 1 fails)

### For PostgreSQL:
```bash
# Connect to your database
psql -U your_username -d your_database_name

# Or if using docker:
docker exec -it your_postgres_container psql -U your_username -d your_database_name
```

Then run:
```sql
ALTER TABLE system_settings 
ADD COLUMN IF NOT EXISTS standard_work_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN IF NOT EXISTS overtime_threshold_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN IF NOT EXISTS half_day_threshold_hours DECIMAL(4,2) DEFAULT 4.00,
ADD COLUMN IF NOT EXISTS lunch_break_duration INTEGER DEFAULT 60,
ADD COLUMN IF NOT EXISTS additional_settings JSON DEFAULT '{}';
```

### For MySQL:
```bash
# Connect to your database
mysql -u your_username -p your_database_name
```

Then run:
```sql
ALTER TABLE system_settings 
ADD COLUMN standard_work_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN overtime_threshold_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN half_day_threshold_hours DECIMAL(4,2) DEFAULT 4.00,
ADD COLUMN lunch_break_duration INT DEFAULT 60,
ADD COLUMN additional_settings JSON DEFAULT (JSON_OBJECT());
```

---

## Option 3: Fix Celery Issue and Run Django Migrations

The Django migrations fail because celery is not installed.

### Quick Fix:
```bash
# Install celery
pip install celery

# Then run migrations
python3 manage.py migrate
```

### OR Temporarily Disable Celery:

Edit `/Users/sandy/projects/python/hrm/hrm_project/__init__.py`:

**Before:**
```python
from .celery import app as celery_app
__all__ = ('celery_app',)
```

**After:**
```python
# Temporarily commented out for migrations
# from .celery import app as celery_app
# __all__ = ('celery_app',)
```

Then run:
```bash
python3 manage.py migrate
```

**Don't forget to uncomment it after migrations!**

---

## Verify the Fix

After adding the columns, verify they exist:

### PostgreSQL:
```sql
\d system_settings
```

### MySQL:
```sql
DESCRIBE system_settings;
```

### Python:
```python
python3 direct_migration.py
# It will show all columns
```

---

## After Adding Columns

1. **Restart Django server**
2. **Go to /settings/** - Should work now!
3. **Run recalculate command**:
   ```bash
   python3 manage.py recalculate_late_status --all
   ```

---

## Quick Summary

**Fastest fix:**
```bash
cd /Users/sandy/projects/python/hrm
python3 direct_migration.py
# Restart Django server
# Visit /settings/
```

**If that doesn't work:**
- Use Option 2 (manual SQL)
- Or Option 3 (fix celery and use Django migrations)

---

## Files Created to Help

- `direct_migration.py` - Automated Python script
- `add_columns.sql` - SQL commands to run manually
- This file - Step-by-step instructions

---

**After this is fixed, the late calculation will work correctly!** ✅
