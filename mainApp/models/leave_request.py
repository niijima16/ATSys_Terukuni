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
    approved_by = models.ManyToManyField(User_Master, related_name='approved_requests', blank=True)  # 承認者リスト
    approved = models.BooleanField(default=False)
    applicant_comment = models.TextField(blank=True, null=True)  # 申請者のコメント
    approver_comment = models.TextField(blank=True, null=True)  # 承認者のコメント

    def save(self, *args, **kwargs):
        # 承認者全員が承認した場合に申請を承認済みにする
        super().save(*args, **kwargs)
        if self.approved_by.count() == self.user.get_superiors().count():
            self.approved = True
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - {self.get_leave_type_display()} ({self.start_date} から {self.end_date})"