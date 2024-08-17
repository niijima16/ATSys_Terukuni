from django.db import models
from .user_master import User_Master
from .time_shift import Shift
from django.utils import timezone

class TimeStamp(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    clock_in_time = models.DateTimeField(default=timezone.now)  # 出勤時間
    clock_out_time = models.DateTimeField(null=True, blank=True)  # 退勤時間

    def calculate_worked_hours(self):
        if self.clock_out_time:
            total_time = self.clock_out_time - self.clock_in_time
            # 休憩時間を考慮して働いた時間を計算
            if self.shift and self.shift.break_time:
                total_time -= self.shift.break_time
            return total_time.total_seconds() / 3600  # 時間単位で返す
        return 0

    def __str__(self):
        return f"{self.user.name} - {self.clock_in_time} to {self.clock_out_time if self.clock_out_time else '未退勤'}"