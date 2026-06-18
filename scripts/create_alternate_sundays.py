import os
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrm_project.settings')
django.setup()

from leaves.models import Holiday

def create_alternate_sundays():
    # Start date as specified by user (Not a holiday)
    start_date = date(2025, 12, 21) 
    
    # Generate for the next 2 years to be safe
    end_date = date(2027, 12, 31)
    
    print(f"🚀 Generating alternate Sunday holidays...")
    print(f"📅 Start Date: {start_date} (Working Sunday)")
    print(f"📅 End Date:   {end_date}")
    print("-" * 50)
    
    current_date = start_date
    is_holiday = False # The anchor date (Dec 21) is NOT a holiday
    
    count_created = 0
    count_skipped = 0
    
    while current_date <= end_date:
        if is_holiday:
            # Create the holiday
            holiday_name = 'Alternate Sunday Off'
            obj, created = Holiday.objects.get_or_create(
                date=current_date,
                defaults={
                    'name': holiday_name,
                    'description': 'Regular alternate Sunday holiday'
                }
            )
            
            status = "✅ Created" if created else "♻️  Exists"
            print(f"{current_date.strftime('%Y-%m-%d (%a)')}: {status} - {holiday_name}")
            count_created += 1
        else:
            print(f"{current_date.strftime('%Y-%m-%d (%a)')}: ⏭️  Skipped (Working Day)")
            count_skipped += 1
            
        # Move to next week
        current_date += timedelta(days=7)
        
        # Toggle pattern
        is_holiday = not is_holiday

    print("-" * 50)
    print(f"✨ Done! Processed {count_created + count_skipped} Sundays.")
    print(f"   - Holidays: {count_created}")
    print(f"   - Working:  {count_skipped}")

if __name__ == '__main__':
    create_alternate_sundays()
