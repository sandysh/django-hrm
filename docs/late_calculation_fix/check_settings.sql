-- SQL Script to Check Both Settings Tables
-- Run this in your database client (psql, mysql, etc.)

-- ============================================
-- Check System Settings Table
-- ============================================
SELECT 
    'SYSTEM SETTINGS' as table_name,
    id,
    office_start_time,
    office_end_time,
    late_threshold_minutes,
    working_days,
    updated_at
FROM system_settings;

-- ============================================
-- Check Attendance Settings Table
-- ============================================
SELECT 
    'ATTENDANCE SETTINGS' as table_name,
    id,
    shift_start_time,
    shift_end_time,
    grace_period_minutes,
    standard_work_hours,
    overtime_threshold_hours,
    half_day_threshold_hours,
    updated_at
FROM attendance_settings;

-- ============================================
-- Show the Mismatch (if any)
-- ============================================
SELECT 
    'COMPARISON' as info,
    ss.office_start_time as system_start_time,
    att.shift_start_time as attendance_start_time,
    CASE 
        WHEN ss.office_start_time = att.shift_start_time THEN '✓ MATCH'
        ELSE '✗ MISMATCH - This was the problem!'
    END as status,
    ss.late_threshold_minutes as system_grace_minutes,
    att.grace_period_minutes as attendance_grace_minutes
FROM system_settings ss
CROSS JOIN attendance_settings att
LIMIT 1;

-- ============================================
-- Check if tables exist
-- ============================================
-- For PostgreSQL:
-- SELECT table_name FROM information_schema.tables 
-- WHERE table_name IN ('system_settings', 'attendance_settings');

-- For MySQL:
-- SHOW TABLES LIKE '%settings%';
