# Generated by Django 5.0.6 on 2024-07-07 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0004_alter_company_department_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user_master',
            name='department',
        ),
        migrations.AlterField(
            model_name='user_master',
            name='user_id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
