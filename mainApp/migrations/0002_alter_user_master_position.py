# Generated by Django 5.0.6 on 2024-07-29 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_master',
            name='position',
            field=models.CharField(choices=[('社員', '平社員'), ('リーダー', 'リーダー'), ('マネージャー', 'マネージャー'), ('課長', '課長'), ('部長', '部長'), ('取締役', '取締役'), ('社長', '社長')], default='社員', max_length=10),
        ),
    ]
