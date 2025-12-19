from django.core.management.base import BaseCommand
from leaves.models import LeaveType


class Command(BaseCommand):
    help = 'Create default leave types'

    def handle(self, *args, **options):
        default_leave_types = [
            {
                'name': 'Annual Leave',
                'code': 'AL',
                'description': 'Annual vacation leave for rest and recreation',
                'default_days': 15,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Sick Leave',
                'code': 'SL',
                'description': 'Leave for medical reasons and health issues',
                'default_days': 10,
                'is_paid': True,
                'requires_approval': False,
            },
            {
                'name': 'Casual Leave',
                'code': 'CL',
                'description': 'Short-term leave for personal matters',
                'default_days': 5,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Maternity Leave',
                'code': 'ML',
                'description': 'Leave for maternity purposes',
                'default_days': 90,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Paternity Leave',
                'code': 'PL',
                'description': 'Leave for paternity purposes',
                'default_days': 15,
                'is_paid': True,
                'requires_approval': True,
            },
            {
                'name': 'Unpaid Leave',
                'code': 'UL',
                'description': 'Leave without pay for extended absences',
                'default_days': 0,
                'is_paid': False,
                'requires_approval': True,
            },
        ]

        created_count = 0
        for leave_data in default_leave_types:
            leave_type, created = LeaveType.objects.get_or_create(
                code=leave_data['code'],
                defaults=leave_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created leave type: {leave_type.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠ Leave type already exists: {leave_type.name}')
                )

        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\n✅ Successfully created {created_count} leave type(s)')
            )
        else:
            self.stdout.write(
                self.style.WARNING('\nℹ️  All default leave types already exist')
            )
