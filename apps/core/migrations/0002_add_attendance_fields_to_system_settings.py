# Generated migration for adding attendance fields to SystemSettings

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='systemsettings',
            name='standard_work_hours',
            field=models.DecimalField(decimal_places=2, default=8.0, help_text='Standard working hours per day', max_digits=4),
        ),
        migrations.AddField(
            model_name='systemsettings',
            name='overtime_threshold_hours',
            field=models.DecimalField(decimal_places=2, default=8.0, help_text='Hours threshold for overtime calculation', max_digits=4),
        ),
        migrations.AddField(
            model_name='systemsettings',
            name='half_day_threshold_hours',
            field=models.DecimalField(decimal_places=2, default=4.0, help_text='Minimum hours for half-day attendance', max_digits=4),
        ),
        migrations.AddField(
            model_name='systemsettings',
            name='lunch_break_duration',
            field=models.IntegerField(default=60, help_text='Lunch break duration in minutes'),
        ),
        migrations.AddField(
            model_name='systemsettings',
            name='additional_settings',
            field=models.JSONField(blank=True, default=dict, help_text='Additional settings in key-value format. Add new settings here without migrations.'),
        ),
    ]
