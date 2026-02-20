-- Simple SQL to fix late status in database
-- Run this in your PostgreSQL database

-- Step 1: Check current settings
SELECT 
    'Current Settings' as info,
    office_start_time,
    late_threshold_minutes,
    office_start_time + (late_threshold_minutes || ' minutes')::interval as grace_time
FROM system_settings
WHERE id = 1;

-- Step 2: Update is_late field based on SystemSettings
UPDATE daily_attendance da
SET is_late = (
    da.check_in_time > (
        SELECT (ss.office_start_time + (ss.late_threshold_minutes || ' minutes')::interval)::time
        FROM system_settings ss
        WHERE ss.id = 1
    )
)
WHERE da.check_in_time IS NOT NULL;

-- Step 3: Update status field based on new is_late value
UPDATE daily_attendance da
SET status = CASE
    WHEN da.total_hours IS NULL OR da.total_hours = 0 THEN da.status
    WHEN da.total_hours < (SELECT half_day_threshold_hours FROM system_settings WHERE id = 1) THEN 'HL'
    WHEN da.is_late THEN 'LT'
    ELSE 'PR'
END
WHERE da.check_in_time IS NOT NULL
  AND da.total_hours IS NOT NULL;

-- Step 4: Show summary
SELECT 
    'Summary' as info,
    COUNT(*) as total_records,
    SUM(CASE WHEN is_late THEN 1 ELSE 0 END) as late_count,
    SUM(CASE WHEN NOT is_late THEN 1 ELSE 0 END) as not_late_count
FROM daily_attendance
WHERE check_in_time IS NOT NULL;

-- Step 5: Show sample records
SELECT 
    e.employee_id,
    da.date,
    da.check_in_time,
    da.is_late,
    da.status,
    ss.office_start_time,
    (ss.office_start_time + (ss.late_threshold_minutes || ' minutes')::interval)::time as grace_time
FROM daily_attendance da
JOIN employees e ON da.employee_id = e.id
CROSS JOIN system_settings ss
WHERE ss.id = 1
  AND da.check_in_time IS NOT NULL
  AND da.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY da.date DESC, da.check_in_time
LIMIT 20;
