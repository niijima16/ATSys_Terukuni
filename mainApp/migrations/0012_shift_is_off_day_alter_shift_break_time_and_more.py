# Generated by Django 5.0.6 on 2024-08-08 14:02

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0011_shift_is_weekend_shift_weekday'),
    ]

    operations = [
        migrations.AddField(
            model_name='shift',
            name='is_off_day',
            field=models.BooleanField(default=False, editable=False),
        ),
        migrations.AlterField(
            model_name='shift',
            name='break_time',
            field=models.DurationField(default=datetime.timedelta(0)),
        ),
        migrations.AlterField(
            model_name='shift',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='shift',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]