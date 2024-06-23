from django.db import models

class Company(models.Model):
    department_id = models.PositiveIntegerField(primary_key=True)
    department = models.CharField(max_length=255)
    position = models.CharField(max_length=255)

    def __str__(self):
        return self.department
