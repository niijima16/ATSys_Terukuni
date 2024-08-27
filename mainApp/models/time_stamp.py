# time_stamp.py

from django.db import models
from .user_master import User_Master
from .time_shift import Shift
from django.utils import timezone
from decimal import ROUND_DOWN
from datetime import datetime

class TimeStamp(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    clock_in_time = models.DateTimeField(default=timezone.now)  # 出勤時間
    clock_out_time = models.DateTimeField(null=True, blank=True)  # 退勤時間

    def calculate_worked_hours(self):
        if self.clock_out_time and self.shift:
            # シフトの開始時間と終了時間をtimezone-awareのdatetime型に変換
            shift_start_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))

            # 実際の出勤時間と退勤時間をシフト内に収める
            clock_in_time = max(self.clock_in_time, shift_start_datetime)
            clock_out_time = min(self.clock_out_time, shift_end_datetime)

            # 勤務時間を計算
            worked_time = clock_out_time - clock_in_time
            
            # 休憩時間を差し引く
            worked_time -= self.shift.break_time

            # 勤務時間を小数点2桁で返す
            worked_hours = worked_time.total_seconds() / 3600
            return round(worked_hours, 2)
        return 0

    def __str__(self):
        return f"{self.user.name} - {self.clock_in_time} to {self.clock_out_time if self.clock_out_time else '未退勤'}"