-- SQL Migration to add new columns to system_settings
-- Run this in your database client (psql, mysql, etc.)

-- Add new columns
ALTER TABLE system_settings 
ADD COLUMN IF NOT EXISTS standard_work_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN IF NOT EXISTS overtime_threshold_hours DECIMAL(4,2) DEFAULT 8.00,
ADD COLUMN IF NOT EXISTS half_day_threshold_hours DECIMAL(4,2) DEFAULT 4.00,
ADD COLUMN IF NOT EXISTS lunch_break_duration INTEGER DEFAULT 60,
ADD COLUMN IF NOT EXISTS additional_settings JSON DEFAULT '{}';

-- Verify the columns were added
SELECT column_name, data_type, column_default 
FROM information_schema.columns 
WHERE table_name = 'system_settings'
ORDER BY ordinal_position;
