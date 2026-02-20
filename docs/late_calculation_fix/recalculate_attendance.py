#!/usr/bin/env python3
"""
Standalone script to recalculate late status for attendance records
Bypasses Django management command to avoid celery dependency
"""
import os
import sys
from datetime import datetime, timedelta, date

def get_db_config():
    """Read database config from .env"""
    env_file = '/Users/sandy/projects/python/hrm/.env'
    config = {}
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value.strip().strip('"').strip("'")
    
    return config

def recalculate_attendance(days=30):
    """Recalculate late status for attendance records"""
    config = get_db_config()
    
    db_engine = config.get('DB_ENGINE', 'postgresql')
    db_name = config.get('DB_NAME')
    db_user = config.get('DB_USER')
    db_password = config.get('DB_PASSWORD')
    db_host = config.get('DB_HOST', 'localhost')
    db_port = config.get('DB_PORT', '5432')
    
    print("=" * 70)
    print("Recalculating Late Status for Attendance Records")
    print("=" * 70)
    print(f"Database: {db_name}")
    print(f"Days to recalculate: {days}")
    print()
    
    if 'postgres' in db_engine.lower():
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            print("✓ Connected to PostgreSQL")
            print()
            
            # Get system settings
            cursor.execute("SELECT * FROM system_settings WHERE id = 1")
            settings = cursor.fetchone()
            
            if not settings:
                print("✗ Error: SystemSettings not found!")
                sys.exit(1)
            
            office_start_time = settings['office_start_time']
            late_threshold_minutes = settings['late_threshold_minutes']
            half_day_threshold = float(settings.get('half_day_threshold_hours', 4.0))
            
            print(f"Using SystemSettings:")
            print(f"  Office Start Time: {office_start_time}")
            print(f"  Late Threshold: {late_threshold_minutes} minutes")
            print(f"  Grace Time: {office_start_time} + {late_threshold_minutes} min")
            print()
            
            # Calculate cutoff date
            cutoff_date = date.today() - timedelta(days=days)
            
            # Get attendance records
            cursor.execute("""
                SELECT id, employee_id, date, check_in_time, total_hours, 
                       is_late, status
                FROM daily_attendance
                WHERE date >= %s AND check_in_time IS NOT NULL
                ORDER BY date DESC
            """, (cutoff_date,))
            
            records = cursor.fetchall()
            total_records = len(records)
            
            print(f"Found {total_records} records to process")
            print()
            
            if total_records == 0:
                print("No records to process!")
                return
            
            # Statistics
            changed_count = 0
            was_late_now_not = 0
            was_not_late_now_is = 0
            
            # Process each record
            for record in records:
                old_is_late = record['is_late']
                old_status = record['status']
                
                # Calculate grace time for this date
                record_date = record['date']
                check_in_time = record['check_in_time']
                
                # Combine date and times for comparison
                grace_datetime = datetime.combine(
                    record_date,
                    office_start_time
                ) + timedelta(minutes=late_threshold_minutes)
                
                check_in_datetime = datetime.combine(record_date, check_in_time)
                
                # Calculate new late status
                new_is_late = check_in_datetime > grace_datetime
                
                # Calculate new status
                new_status = old_status
                total_hours = float(record['total_hours']) if record['total_hours'] else 0
                
                if total_hours:
                    if total_hours < half_day_threshold:
                        new_status = 'HL'  # Half day
                    elif new_is_late:
                        new_status = 'LT'  # Late
                    else:
                        new_status = 'PR'  # Present
                
                # Check if changed
                if old_is_late != new_is_late or old_status != new_status:
                    changed_count += 1
                    
                    if old_is_late and not new_is_late:
                        was_late_now_not += 1
                    elif not old_is_late and new_is_late:
                        was_not_late_now_is += 1
                    
                    # Get employee ID for display
                    cursor.execute(
                        "SELECT employee_id FROM employees WHERE id = %s",
                        (record['employee_id'],)
                    )
                    emp_result = cursor.fetchone()
                    emp_id = emp_result['employee_id'] if emp_result else f"ID:{record['employee_id']}"
                    
                    print(f"{emp_id} | {record_date} | {check_in_time} | "
                          f"Late: {old_is_late} → {new_is_late} | "
                          f"Status: {old_status} → {new_status}")
                    
                    # Update the record
                    cursor.execute("""
                        UPDATE daily_attendance
                        SET is_late = %s, status = %s
                        WHERE id = %s
                    """, (new_is_late, new_status, record['id']))
            
            # Commit changes
            conn.commit()
            
            # Summary
            print()
            print("=" * 70)
            print("SUMMARY")
            print("=" * 70)
            print(f"Total records processed: {total_records}")
            print(f"Records changed: {changed_count}")
            print(f"  - Was late, now not late: {was_late_now_not}")
            print(f"  - Was not late, now late: {was_not_late_now_is}")
            print()
            print("✓ All changes saved successfully!")
            print()
            print("Next steps:")
            print("1. Refresh your dashboard")
            print("2. Check attendance reports")
            print("3. Verify users punching in at 10:00 AM are NOT marked late")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    else:
        print(f"✗ Unsupported database engine: {db_engine}")
        print("This script currently supports PostgreSQL only")
        sys.exit(1)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Recalculate late status for attendance records')
    parser.add_argument('--days', type=int, default=30, help='Number of days to recalculate (default: 30)')
    parser.add_argument('--all', action='store_true', help='Recalculate all records')
    
    args = parser.parse_args()
    
    days = 99999 if args.all else args.days
    
    recalculate_attendance(days)
