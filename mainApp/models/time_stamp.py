from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta
from mainApp.models.user_master import User_Master
from mainApp.models.time_shift import Shift

class TimeStamp(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE, null=True, blank=True)
    clock_in_time = models.DateTimeField(default=timezone.now)  # 出勤時間
    clock_out_time = models.DateTimeField(null=True, blank=True)  # 退勤時間

    def calculate_worked_hours(self):
        if self.clock_out_time and self.shift:
            shift_start_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))

            clock_in_time = max(self.clock_in_time, shift_start_datetime)
            clock_out_time = min(self.clock_out_time, shift_end_datetime)

            worked_time = clock_out_time - clock_in_time
            worked_time -= self.shift.break_time

            return round(worked_time.total_seconds() / 3600, 2)
        return 0

    def calculate_overtime(self):
        if self.clock_out_time and self.shift:
            shift_start_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))

            clock_in_time = max(self.clock_in_time, shift_start_datetime)
            clock_out_time = min(self.clock_out_time, shift_end_datetime)

            if self.clock_in_time < shift_start_datetime:
                clock_in_time = shift_start_datetime
            if self.clock_out_time > shift_end_datetime:
                clock_out_time = shift_end_datetime

            regular_hours = shift_end_datetime - shift_start_datetime
            worked_time = clock_out_time - clock_in_time

            if worked_time > regular_hours:
                overtime = worked_time - regular_hours
                return round(overtime.total_seconds() / 3600, 2)
            return 0
        return 0

    def calculate_early_leave(self):
        if self.clock_out_time and self.shift:
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))

            clock_out_time = min(self.clock_out_time, shift_end_datetime)

            if self.clock_out_time < shift_end_datetime:
                early_leave = shift_end_datetime - clock_out_time
                return round(early_leave.total_seconds() / 3600, 2)
            return 0
        return 0

    def __str__(self):
        return f"{self.user.name} - {self.clock_in_time} to {self.clock_out_time if self.clock_out_time else '未退勤'}"