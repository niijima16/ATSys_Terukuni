from django.db import models

# Create your models here.
class uerInfo(models.Model):
    name = models.CharField(max_length=32)
    passwd = models.CharField(max_length=64)
    age = models.IntegerField(default=20)
    size = models.IntegerField(null=True, blank=True)


class Department(models.Model):
    title = models.CharField(max_length=16)
