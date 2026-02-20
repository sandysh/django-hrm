# Final Solution: Fix Database Late Status

## What Was Done

✅ **Reverted templates** - Back to using database `is_late` field  
✅ **Created SQL script** - To fix database values  

## The Problem

The database has old `is_late` values calculated with the wrong settings (9am start time).

## The Solution

Run SQL to update the database with correct values based on SystemSettings (10am start time).

## How to Fix

### Option 1: Run SQL Script (Recommended)

**Connect to your database:**
```bash
# For PostgreSQL
psql -U your_username -d your_database_name

# Or if using Docker
docker exec -it your_postgres_container psql -U your_username -d your_database_name
```

**Run the SQL file:**
```sql
\i /Users/sandy/projects/python/hrm/fix_database_late_status.sql
```

**Or copy-paste this SQL:**
```sql
-- Update is_late based on SystemSettings
UPDATE daily_attendance da
SET is_late = (
    da.check_in_time > (
        SELECT (ss.office_start_time + (ss.late_threshold_minutes || ' minutes')::interval)::time
        FROM system_settings ss
        WHERE ss.id = 1
    )
)
WHERE da.check_in_time IS NOT NULL;

-- Update status based on new is_late
UPDATE daily_attendance da
SET status = CASE
    WHEN da.total_hours IS NULL OR da.total_hours = 0 THEN da.status
    WHEN da.total_hours < (SELECT half_day_threshold_hours FROM system_settings WHERE id = 1) THEN 'HL'
    WHEN da.is_late THEN 'LT'
    ELSE 'PR'
END
WHERE da.check_in_time IS NOT NULL AND da.total_hours IS NOT NULL;
```

### Option 2: Use Database GUI

If you have a database GUI (pgAdmin, DBeaver, etc.):

1. Open your database
2. Open SQL query window
3. Paste the SQL from `fix_database_late_status.sql`
4. Execute

## After Running SQL

1. **Refresh your browser**
2. **Check attendance report**
3. **10am punch-ins should show as "Present" (not "Late")**

## Verify It Worked

Run this query to check:
```sql
SELECT 
    e.employee_id,
    da.date,
    da.check_in_time,
    da.is_late,
    da.status
FROM daily_attendance da
JOIN employees e ON da.employee_id = e.id
WHERE da.check_in_time BETWEEN '10:00:00' AND '10:15:00'
  AND da.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY da.date DESC;
```

**Expected result:** All records with check_in between 10:00-10:15 should have `is_late = false`

## Summary

**Before:**
- Templates: Using on-the-fly calculation ❌
- Database: Has wrong values ❌

**After:**
- Templates: Using database field ✅
- Database: Fixed with SQL ✅

---

**Just run the SQL and you're done!** 🎉

Files:
- `fix_database_late_status.sql` - Complete SQL script
- This guide - Instructions
