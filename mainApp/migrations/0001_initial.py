# Generated by Django 5.0.6 on 2024-07-14 11:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='COMPANY',
            fields=[
                ('department_id', models.PositiveIntegerField(default='1', editable=False, primary_key=True, serialize=False, unique=True)),
                ('department', models.CharField(max_length=255)),
                ('position', models.CharField(default='正社員', max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='User_Master',
            fields=[
                ('user_id', models.PositiveIntegerField(editable=False, primary_key=True, serialize=False, unique=True)),
                ('account_id', models.EmailField(max_length=255, unique=True)),
                ('password', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255)),
                ('age', models.PositiveSmallIntegerField()),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1)),
                ('phone_number', models.CharField(max_length=11)),
                ('joined', models.DateField()),
                ('department_name', models.CharField(max_length=255)),
                ('position', models.CharField(default='正社員', max_length=255)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.company')),
            ],
        ),
        migrations.CreateModel(
            name='time_sheet',
            fields=[
                ('timeSheet_id', models.AutoField(primary_key=True, serialize=False)),
                ('start', models.DateField()),
                ('end', models.DateField()),
                ('day_off', models.DateField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.user_master')),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceEvent',
            fields=[
                ('at_id', models.AutoField(primary_key=True, serialize=False)),
                ('number_of_work', models.IntegerField()),
                ('timeSheet', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.time_sheet')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mainApp.user_master')),
            ],
        ),
    ]
