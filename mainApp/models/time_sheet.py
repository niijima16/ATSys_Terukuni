from django.db import models
from datetime import timedelta

class TimeSheet(models.Model):
    user = models.ForeignKey('User_Master', on_delete=models.CASCADE)  # User_Masterを使用
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_time = models.DurationField(default=timedelta(minutes=0))
    overtime = models.DurationField(default=timedelta(minutes=0))
    leave_type = models.ForeignKey('LeaveType', on_delete=models.SET_NULL, null=True, blank=True)
    comments = models.TextField(blank=True)

    class Meta:
        verbose_name = 'タイムシート'
        verbose_name_plural = 'タイムシート'
        unique_together = ('user', 'date')  # 同じ日に同じユーザーが複数のタイムシートを持たないようにする

    def __str__(self):
        return f"{self.user.name} - {self.date}"  # User_Masterモデルのnameフィールドを使用

    @property
    def total_work_time(self):
        # 実働時間を計算
        work_duration = (self.end_time - self.start_time) - self.break_time
        if work_duration < timedelta(0):
            work_duration += timedelta(days=1)
        return work_duration