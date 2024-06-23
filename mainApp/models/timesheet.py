from django.db import models
from .user_master import UserMaster

class Timesheet(models.Model):
    timesheet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    dayoff = models.DateField()

    def __str__(self):
        return f"Timesheet {self.timesheet_id} for {self.user.name}"
