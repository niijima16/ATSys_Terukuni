from django.db import models
from .timesheet import Timesheet
from .user_master import UserMaster

class AttendanceEvent(models.Model):
    at_id = models.AutoField(primary_key=True)
    number_of_work = models.IntegerField()
    account = models.ForeignKey(UserMaster, on_delete=models.CASCADE)
    timesheet = models.ForeignKey(Timesheet, on_delete=models.CASCADE)

    def __str__(self):
        return f"Attendance {self.at_id} for {self.account.name}"
