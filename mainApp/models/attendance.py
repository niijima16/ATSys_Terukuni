from django.db import models
from django.utils import timezone
from .user_master import User_Master
from .leave_type import LeaveType

class Attendance(models.Model):
    STATUS_CHOICES = [
        ('present', '出勤'),
        ('absent', '欠勤'),
        ('vacation', '休暇'),
        ('sick', '病欠'),
    ]

    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='present')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('user', 'date')
        verbose_name = '勤怠'
        verbose_name_plural = '勤怠'

    def __str__(self):
        return f"{self.user.name} - {self.date} - {self.get_status_display()}"