from django.core.management.base import BaseCommand
from reports.models import TaxSlab

class Command(BaseCommand):
    help = 'Seeds the database with initial tax slabs from the provided bands.'

    def handle(self, *args, **kwargs):
        # Data to be seeded
        slabs_data = [
            {'name': 'Band 1', 'min_salary': 0, 'max_salary': 500000, 'tax_rate': 1},
            {'name': 'Band 2', 'min_salary': 500001, 'max_salary': 700000, 'tax_rate': 10},
            {'name': 'Band 3', 'min_salary': 700001, 'max_salary': 1000000, 'tax_rate': 20},
            {'name': 'Band 4', 'min_salary': 1000001, 'max_salary': 2000000, 'tax_rate': 30},
            {'name': 'Band 5', 'min_salary': 2000001, 'max_salary': 5000000, 'tax_rate': 36},
            {'name': 'Additional Tax', 'min_salary': 5000001, 'max_salary': 9999999999.0, 'tax_rate': 39},
        ]

        self.stdout.write('Clearing existing tax slabs...')
        TaxSlab.objects.all().delete()

        self.stdout.write('Seeding new tax slabs...')
        for slab_data in slabs_data:
            TaxSlab.objects.create(**slab_data)
            self.stdout.write(self.style.SUCCESS(f"Successfully created {slab_data['name']} (Rate: {slab_data['tax_rate']}%)"))

        self.stdout.write(self.style.SUCCESS('Finished seeding tax slabs!'))
