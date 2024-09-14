# models/leave_request.py

from django.db import models
from .user_master import User_Master

class LeaveRequest(models.Model):
    LEAVE_TYPE_CHOICES = [
        ('Paid', '有給'),
        ('Sick', '病気'),
        ('PersonalMatter', '私事'),
    ]

    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=50, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    is_paid_leave = models.BooleanField(default=False)  # 有給かどうかのフラグ
    approved = models.BooleanField(default=False)
    applicant_comment = models.TextField(blank=True, null=True)  # 申請者のコメント
    approver_comment = models.TextField(blank=True, null=True)  # 承認者のコメント

    def __str__(self):
        return f"{self.user.name} - {self.get_leave_type_display()} ({self.start_date} から {self.end_date})"