# models/leave_request.py

from django.db import models
from .user_master import User_Master

class LeaveRequest(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50)  # 例: '有給', '病気', '無給' など
    start_date = models.DateField()
    end_date = models.DateField()
    approved = models.BooleanField(default=False)
    is_paid_leave = models.BooleanField(default=False)  # 有給休暇かどうかのフラグ

    def __str__(self):
        return f"{self.user.name} - {self.leave_type} ({self.start_date} から {self.end_date})"