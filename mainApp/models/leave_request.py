from django.db import models
from .user_master import User_Master
from .leave_type import LeaveType

class LeaveRequest(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField(blank=True)
    approved = models.BooleanField(default=False)

    class Meta:
        verbose_name = '休暇リクエスト'
        verbose_name_plural = '休暇リクエスト'

    def __str__(self):
        return f"{self.user.name} - {self.leave_type.name} ({self.start_date} to {self.end_date})"