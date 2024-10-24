# Generated by Django 5.0.6 on 2024-07-30 13:41

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0004_leavetype_remove_time_sheet_user_leaverequest_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimeSheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('break_time', models.DurationField(default=datetime.timedelta(0))),
                ('overtime', models.DurationField(default=datetime.timedelta(0))),
                ('comments', models.TextField(blank=True)),
                ('leave_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='mainApp.leavetype')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.user_master')),
            ],
            options={
                'verbose_name': 'タイムシート',
                'verbose_name_plural': 'タイムシート',
                'unique_together': {('user', 'date')},
            },
        ),
    ]
