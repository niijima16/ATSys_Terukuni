# Generated by Django 5.0.6 on 2024-07-06 07:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0002_alter_company_department_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_master',
            name='position',
            field=models.CharField(default='正社員', max_length=255),
        ),
        migrations.AlterField(
            model_name='company',
            name='position',
            field=models.CharField(default='正社員', max_length=255),
        ),
    ]
