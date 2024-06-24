from django.db import models
from .user_master import User_Master

class time_sheet(models.Model):
    timeSheet_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    start = models.DateField()
    end = models.DateField()
    day_off = models.DateField()

    def __str__(self):
        return f"time_sheet {self.timeSheet_id} for {self.user.name}"
