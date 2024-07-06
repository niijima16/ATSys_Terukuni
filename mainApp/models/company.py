from django.db import models

class COMPANY(models.Model):
    department_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False,default='1')
    department = models.CharField(max_length=255)
    position = models.CharField(max_length=255, default='正社員')

    def __str__(self):
        return self.department
