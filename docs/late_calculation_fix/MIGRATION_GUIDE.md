# Migration Guide: Removing AttendanceSettings

## Overview
This guide explains how to migrate from the duplicate `AttendanceSettings` model to the consolidated `SystemSettings` model.

## What Changed

### Before
- **Two settings models**: `SystemSettings` (core) and `AttendanceSettings` (attendance)
- Settings were split and not synchronized
- Confusion about which settings were actually being used

### After
- **One settings model**: `SystemSettings` (core)
- All attendance-related settings consolidated
- Single source of truth for all system settings

## Migration Steps

### Automatic Migration (Recommended)

Run the migrations in order:

```bash
cd /Users/sandy/projects/python/hrm

# 1. Add new fields to SystemSettings
python manage.py migrate core 0002_add_attendance_fields_to_system_settings

# 2. Copy data from AttendanceSettings to SystemSettings
python manage.py migrate core 0003_migrate_attendance_settings_data

# 3. Remove AttendanceSettings model and table
python manage.py migrate attendance 0002_remove_attendance_settings

# Or run all at once:
python manage.py migrate
```

### Manual Migration (If needed)

If automatic migration fails, you can migrate manually:

```sql
-- 1. Add new columns to system_settings
ALTER TABLE system_settings 
ADD COLUMN standard_work_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN overtime_threshold_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN half_day_threshold_hours DECIMAL(4,2) DEFAULT 4.00,
ADD COLUMN lunch_break_duration INTEGER DEFAULT 60;

-- 2. Copy data from attendance_settings to system_settings (if exists)
UPDATE system_settings ss
SET 
    standard_work_hours = (SELECT standard_work_hours FROM attendance_settings LIMIT 1),
    overtime_threshold_hours = (SELECT overtime_threshold_hours FROM attendance_settings LIMIT 1),
    half_day_threshold_hours = (SELECT half_day_threshold_hours FROM attendance_settings LIMIT 1),
    lunch_break_duration = (SELECT lunch_break_duration FROM attendance_settings LIMIT 1),
    office_start_time = (SELECT shift_start_time FROM attendance_settings LIMIT 1),
    office_end_time = (SELECT shift_end_time FROM attendance_settings LIMIT 1),
    late_threshold_minutes = (SELECT grace_period_minutes FROM attendance_settings LIMIT 1)
WHERE EXISTS (SELECT 1 FROM attendance_settings);

-- 3. Drop the attendance_settings table
DROP TABLE attendance_settings;
```

## Verification

After migration, verify everything is working:

### 1. Check SystemSettings
```bash
python manage.py shell
```

```python
from core.models import SystemSettings
settings = SystemSettings.get_settings()

print(f"Office Start: {settings.office_start_time}")
print(f"Late Threshold: {settings.late_threshold_minutes} min")
print(f"Standard Hours: {settings.standard_work_hours}")
print(f"Overtime Threshold: {settings.overtime_threshold_hours}")
print(f"Half Day Threshold: {settings.half_day_threshold_hours}")
print(f"Lunch Break: {settings.lunch_break_duration} min")
```

### 2. Check Database
```sql
-- Verify system_settings has all fields
SELECT * FROM system_settings;

-- Verify attendance_settings table is gone
SELECT * FROM attendance_settings;  -- Should error: table doesn't exist
```

### 3. Test the Application
```bash
# Start the server
python manage.py runserver

# Test:
# 1. Go to Settings page - should show all settings
# 2. Update office start time
# 3. Have someone punch in
# 4. Verify late calculation works correctly
```

## What Was Migrated

| Old (AttendanceSettings) | New (SystemSettings) |
|-------------------------|---------------------|
| `shift_start_time` | `office_start_time` |
| `shift_end_time` | `office_end_time` |
| `grace_period_minutes` | `late_threshold_minutes` |
| `standard_work_hours` | `standard_work_hours` ✓ |
| `overtime_threshold_hours` | `overtime_threshold_hours` ✓ |
| `half_day_threshold_hours` | `half_day_threshold_hours` ✓ |
| `lunch_break_duration` | `lunch_break_duration` ✓ |

## Files Changed

### Models
- ✅ `core/models.py` - Added attendance fields to SystemSettings
- ✅ `attendance/models.py` - Removed AttendanceSettings model

### Views & Serializers
- ✅ `attendance/views.py` - Removed AttendanceSettingsViewSet
- ✅ `attendance/serializers.py` - Removed AttendanceSettingsSerializer
- ✅ `attendance/urls.py` - Removed settings endpoint
- ✅ `attendance/admin.py` - Removed AttendanceSettingsAdmin
- ✅ `attendance/web_views.py` - Updated imports
- ✅ `core/views.py` - Updated imports

### Tasks & Commands
- ✅ `biometric/tasks.py` - Now uses SystemSettings for all calculations
- ✅ `employees/management/commands/init_hrm.py` - Uses SystemSettings

### Migrations
- ✅ `core/migrations/0002_add_attendance_fields_to_system_settings.py`
- ✅ `core/migrations/0003_migrate_attendance_settings_data.py`
- ✅ `attendance/migrations/0002_remove_attendance_settings.py`

## Rollback (If Needed)

If you need to rollback:

```bash
# Rollback attendance migration
python manage.py migrate attendance 0001_initial

# Rollback core migrations
python manage.py migrate core 0001_initial
```

**Note**: This will lose any settings changes made after migration!

## Troubleshooting

### Issue: Migration fails with "table already exists"
**Solution**: The table might already be dropped. Skip to the next migration.

### Issue: Data not migrated
**Solution**: Run the data migration manually using SQL above.

### Issue: Settings page doesn't show new fields
**Solution**: 
1. Clear browser cache
2. Restart Django server
3. Check that templates are using SystemSettings

### Issue: Late calculation still wrong
**Solution**:
1. Verify SystemSettings has correct values
2. Run recalculate command: `python manage.py recalculate_late_status`
3. Check biometric/tasks.py is using SystemSettings

## Post-Migration Tasks

1. **Update Settings Page** (if needed):
   - Add UI fields for new settings (overtime, half-day thresholds, lunch break)
   - Currently only office hours and late threshold are shown

2. **Recalculate Existing Attendance**:
   ```bash
   python manage.py recalculate_late_status --all
   ```

3. **Update Documentation**:
   - Update any documentation mentioning AttendanceSettings
   - Update API documentation

4. **Clean Up**:
   - Remove check_settings.py (was for debugging)
   - Archive old documentation files

## Benefits of This Change

✅ **Single Source of Truth**: All settings in one place  
✅ **No More Confusion**: Settings page changes actually apply  
✅ **Easier Maintenance**: One model to manage  
✅ **Better UX**: Admins see all settings together  
✅ **Consistent Behavior**: Late calculation uses configured settings  

## Support

If you encounter any issues during migration:
1. Check the troubleshooting section above
2. Review migration logs
3. Check database state with SQL queries
4. Verify all code changes were applied

---

**Migration created**: 2025-12-22  
**Status**: Ready to apply  
**Risk Level**: Low (data is preserved, can rollback)
