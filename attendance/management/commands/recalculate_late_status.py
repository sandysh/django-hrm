"""
Management command to recalculate late status for existing attendance records.
This is useful after fixing the late calculation logic to use SystemSettings.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
from attendance.models import DailyAttendance
from core.models import SystemSettings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Recalculate late status for existing attendance records using SystemSettings'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to recalculate (default: 30)',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Recalculate all attendance records',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually updating',
        )

    def handle(self, *args, **options):
        days = options['days']
        all_records = options['all']
        dry_run = options['dry_run']
        
        # Get system settings
        system_settings = SystemSettings.get_settings()
        
        self.stdout.write(self.style.SUCCESS(
            f'\nUsing SystemSettings:'
        ))
        self.stdout.write(f'  Office Start Time: {system_settings.office_start_time}')
        self.stdout.write(f'  Late Threshold: {system_settings.late_threshold_minutes} minutes')
        self.stdout.write(f'  Grace Time: {system_settings.office_start_time} + {system_settings.late_threshold_minutes} min\n')
        
        # Get attendance records to recalculate
        if all_records:
            attendance_records = DailyAttendance.objects.filter(
                check_in_time__isnull=False
            ).order_by('-date')
            self.stdout.write(f'Recalculating ALL attendance records...\n')
        else:
            cutoff_date = timezone.now().date() - timedelta(days=days)
            attendance_records = DailyAttendance.objects.filter(
                date__gte=cutoff_date,
                check_in_time__isnull=False
            ).order_by('-date')
            self.stdout.write(f'Recalculating attendance records from last {days} days...\n')
        
        total_records = attendance_records.count()
        self.stdout.write(f'Found {total_records} records to process\n')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be saved\n'))
        
        # Statistics
        changed_count = 0
        was_late_now_not = 0
        was_not_late_now_is = 0
        
        for record in attendance_records:
            old_is_late = record.is_late
            old_status = record.status
            
            # Calculate new late status
            grace_time = datetime.combine(
                record.date,
                system_settings.office_start_time
            ) + timedelta(minutes=system_settings.late_threshold_minutes)
            
            check_in_dt = datetime.combine(record.date, record.check_in_time)
            new_is_late = check_in_dt > grace_time
            
            # Update status if needed
            new_status = old_status
            if record.total_hours:
                if record.total_hours < 4.00:  # Half day threshold
                    new_status = 'HL'
                elif new_is_late:
                    new_status = 'LT'
                else:
                    new_status = 'PR'
            
            # Check if changed
            if old_is_late != new_is_late or old_status != new_status:
                changed_count += 1
                
                if old_is_late and not new_is_late:
                    was_late_now_not += 1
                elif not old_is_late and new_is_late:
                    was_not_late_now_is += 1
                
                self.stdout.write(
                    f'{record.employee.employee_id} | {record.date} | '
                    f'{record.check_in_time} | '
                    f'Late: {old_is_late} → {new_is_late} | '
                    f'Status: {old_status} → {new_status}'
                )
                
                if not dry_run:
                    record.is_late = new_is_late
                    record.status = new_status
                    record.save()
        
        # Summary
        self.stdout.write(self.style.SUCCESS(f'\n{"="*60}'))
        self.stdout.write(self.style.SUCCESS('SUMMARY'))
        self.stdout.write(self.style.SUCCESS(f'{"="*60}'))
        self.stdout.write(f'Total records processed: {total_records}')
        self.stdout.write(f'Records changed: {changed_count}')
        self.stdout.write(f'  - Was late, now not late: {was_late_now_not}')
        self.stdout.write(f'  - Was not late, now late: {was_not_late_now_is}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - No changes were saved'))
            self.stdout.write('Run without --dry-run to apply changes')
        else:
            self.stdout.write(self.style.SUCCESS('\n✓ All changes saved successfully!'))
