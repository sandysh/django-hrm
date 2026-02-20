-- SQL Script to Recalculate Late Status
-- Run this in your PostgreSQL database

-- First, check current settings
SELECT 
    'Current Settings:' as info,
    office_start_time,
    late_threshold_minutes,
    (office_start_time::time + (late_threshold_minutes || ' minutes')::interval) as grace_time
FROM system_settings
WHERE id = 1;

-- Show sample of records that will be updated
SELECT 
    'Sample Records (Before Update):' as info,
    da.date,
    da.check_in_time,
    da.is_late as current_is_late,
    da.status as current_status,
    (da.check_in_time > (ss.office_start_time::time + (ss.late_threshold_minutes || ' minutes')::interval)) as should_be_late
FROM daily_attendance da
CROSS JOIN system_settings ss
WHERE ss.id = 1
  AND da.check_in_time IS NOT NULL
  AND da.date >= CURRENT_DATE - INTERVAL '30 days'
LIMIT 10;

-- Update is_late based on SystemSettings
UPDATE daily_attendance da
SET is_late = (
    da.check_in_time > (
        SELECT (office_start_time::time + (late_threshold_minutes || ' minutes')::interval)
        FROM system_settings
        WHERE id = 1
    )
)
WHERE da.check_in_time IS NOT NULL
  AND da.date >= CURRENT_DATE - INTERVAL '30 days';

-- Update status based on new is_late value
UPDATE daily_attendance da
SET status = CASE
    WHEN da.total_hours < (SELECT half_day_threshold_hours FROM system_settings WHERE id = 1) THEN 'HL'
    WHEN da.is_late THEN 'LT'
    ELSE 'PR'
END
WHERE da.check_in_time IS NOT NULL
  AND da.total_hours IS NOT NULL
  AND da.date >= CURRENT_DATE - INTERVAL '30 days';

-- Show summary of changes
SELECT 
    'Summary:' as info,
    COUNT(*) as total_records,
    SUM(CASE WHEN is_late THEN 1 ELSE 0 END) as late_count,
    SUM(CASE WHEN NOT is_late THEN 1 ELSE 0 END) as not_late_count,
    SUM(CASE WHEN status = 'LT' THEN 1 ELSE 0 END) as late_status_count,
    SUM(CASE WHEN status = 'PR' THEN 1 ELSE 0 END) as present_status_count
FROM daily_attendance
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
  AND check_in_time IS NOT NULL;

-- Show sample of updated records
SELECT 
    'Sample Records (After Update):' as info,
    e.employee_id,
    da.date,
    da.check_in_time,
    da.is_late,
    da.status,
    ss.office_start_time,
    (ss.office_start_time::time + (ss.late_threshold_minutes || ' minutes')::interval) as grace_time
FROM daily_attendance da
JOIN employees e ON da.employee_id = e.id
CROSS JOIN system_settings ss
WHERE ss.id = 1
  AND da.check_in_time IS NOT NULL
  AND da.date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY da.date DESC, da.check_in_time
LIMIT 20;
