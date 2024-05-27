from django.db import models

# Create your models here.
class user_master(models.Model):
    user_id = models.AutoField(primary_key=True)
    pwd = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    age = models.PositiveSmallIntegerField()  # charint(4)に対応するフィールド
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=11)  # charint(11)に対応するフィールド
    joined = models.DateField()
    department_id = models.IntegerField()
    department = models.CharField(max_length=256)


class Department(models.Model):
    title = models.CharField(max_length=16)
