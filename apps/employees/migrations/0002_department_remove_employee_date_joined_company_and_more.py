# Generated migration - custom to handle data conversion

from django.db import migrations, models
import django.db.models.deletion


def convert_departments_and_designations(apps, schema_editor):
    """Convert existing department/designation strings to FK relationships."""
    Employee = apps.get_model('employees', 'Employee')
    Department = apps.get_model('employees', 'Department')
    Designation = apps.get_model('employees', 'Designation')
    
    # Get all unique departments from employees
    departments = set()
    designations = set()
    
    for emp in Employee.objects.all():
        if emp.department:
            departments.add(emp.department)
        if emp.designation:
            designations.add(emp.designation)
    
    # Create Department objects
    dept_map = {}
    for dept_name in departments:
        if dept_name:
            dept, created = Department.objects.get_or_create(
                name=dept_name,
                defaults={'code': dept_name[:20].upper().replace(' ', '_')}
            )
            dept_map[dept_name] = dept.id
    
    # Create Designation objects
    desig_map = {}
    for desig_name in designations:
        if desig_name:
            desig, created = Designation.objects.get_or_create(
                name=desig_name,
                defaults={'code': desig_name[:20].upper().replace(' ', '_')}
            )
            desig_map[desig_name] = desig.id


class Migration(migrations.Migration):

    dependencies = [
        ('employees', '0001_initial'),
    ]

    operations = [
        # Create Department model
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        # Create Designation model
        migrations.CreateModel(
            name='Designation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('code', models.CharField(max_length=20, unique=True)),
                ('description', models.TextField(blank=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='designations', to='employees.department')),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        # Convert existing data
        migrations.RunPython(convert_departments_and_designations, reverse_code=migrations.RunPython.noop),
        # Rename old fields
        migrations.RenameField(
            model_name='employee',
            old_name='department',
            new_name='department_old',
        ),
        migrations.RenameField(
            model_name='employee',
            old_name='designation',
            new_name='designation_old',
        ),
        # Add new FK fields
        migrations.AddField(
            model_name='employee',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='employees.department'),
        ),
        migrations.AddField(
            model_name='employee',
            name='designation',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='employees.designation'),
        ),
        # Remove old fields
        migrations.RemoveField(
            model_name='employee',
            name='department_old',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='designation_old',
        ),
    ]
