#!/usr/bin/env python3
"""
Direct database migration script - bypasses Django to add columns
"""
import os
import sys

# Get database connection details from .env
def get_db_config():
    env_file = '/Users/sandy/projects/python/hrm/.env'
    config = {}
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                config[key] = value.strip().strip('"').strip("'")
    
    return config

def run_migration():
    config = get_db_config()
    
    db_engine = config.get('DB_ENGINE', 'postgresql')
    db_name = config.get('DB_NAME')
    db_user = config.get('DB_USER')
    db_password = config.get('DB_PASSWORD')
    db_host = config.get('DB_HOST', 'localhost')
    db_port = config.get('DB_PORT', '5432')
    
    print("=" * 60)
    print("Direct Database Migration")
    print("=" * 60)
    print(f"Database: {db_name}")
    print(f"Host: {db_host}:{db_port}")
    print(f"User: {db_user}")
    print()
    
    # SQL to add columns
    sql_commands = [
        "ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS standard_work_hours DECIMAL(4,2) DEFAULT 8.00;",
        "ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS overtime_threshold_hours DECIMAL(4,2) DEFAULT 8.00;",
        "ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS half_day_threshold_hours DECIMAL(4,2) DEFAULT 4.00;",
        "ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS lunch_break_duration INTEGER DEFAULT 60;",
        "ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS additional_settings JSON DEFAULT '{}';",
    ]
    
    if 'postgres' in db_engine.lower():
        import psycopg2
        
        try:
            conn = psycopg2.connect(
                dbname=db_name,
                user=db_user,
                password=db_password,
                host=db_host,
                port=db_port
            )
            cursor = conn.cursor()
            
            print("✓ Connected to PostgreSQL")
            print()
            
            for sql in sql_commands:
                print(f"Running: {sql[:60]}...")
                cursor.execute(sql)
            
            conn.commit()
            print()
            print("✓ All columns added successfully!")
            
            # Verify
            cursor.execute("""
                SELECT column_name, data_type, column_default 
                FROM information_schema.columns 
                WHERE table_name = 'system_settings'
                ORDER BY ordinal_position
            """)
            
            print()
            print("Columns in system_settings:")
            print("-" * 60)
            for row in cursor.fetchall():
                print(f"  {row[0]:<30} {row[1]:<20} {row[2]}")
            
            cursor.close()
            conn.close()
            
            print()
            print("=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            print()
            print("Next step: Restart your Django server and try accessing /settings/")
            
        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    elif 'mysql' in db_engine.lower():
        import pymysql
        
        # Convert PostgreSQL JSON to MySQL JSON
        sql_commands[-1] = "ALTER TABLE system_settings ADD COLUMN IF NOT EXISTS additional_settings JSON DEFAULT (JSON_OBJECT());"
        
        try:
            conn = pymysql.connect(
                host=db_host,
                port=int(db_port),
                user=db_user,
                password=db_password,
                database=db_name
            )
            cursor = conn.cursor()
            
            print("✓ Connected to MySQL")
            print()
            
            for sql in sql_commands:
                print(f"Running: {sql[:60]}...")
                try:
                    cursor.execute(sql)
                except Exception as e:
                    if 'Duplicate column name' in str(e):
                        print(f"  (Column already exists, skipping)")
                    else:
                        raise
            
            conn.commit()
            print()
            print("✓ All columns added successfully!")
            
            cursor.close()
            conn.close()
            
            print()
            print("=" * 60)
            print("✓ Migration completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)
    
    else:
        print(f"✗ Unsupported database engine: {db_engine}")
        print()
        print("Please run the SQL manually:")
        print()
        for sql in sql_commands:
            print(sql)
        sys.exit(1)

if __name__ == '__main__':
    run_migration()
