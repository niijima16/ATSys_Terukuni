from django.db import models
from .time_sheet import time_sheet
from .user_master import User_Master

class AttendanceEvent(models.Model):
    at_id = models.AutoField(primary_key=True)
    number_of_work = models.IntegerField()
    account = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    timeSheet = models.ForeignKey(time_sheet, on_delete=models.CASCADE)

    def __str__(self):
        return f"Attendance {self.at_id} for {self.account.name}"
