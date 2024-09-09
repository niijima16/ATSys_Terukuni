# time_stamp.py

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
        """
        Calculates the total worked hours for this timestamp.
        """
        if self.clock_out_time and self.shift:
            shift_start_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))

            clock_in_time = max(self.clock_in_time, shift_start_datetime)
            clock_out_time = min(self.clock_out_time, shift_end_datetime)

            # Calculate the worked hours minus the break time
            worked_time = clock_out_time - clock_in_time - self.shift.break_time
            return max(round(worked_time.total_seconds() / 3600, 2), 0)  # Make sure it's non-negative
        return 0

    def calculate_overtime(self):
        """
        Calculates the overtime hours for this timestamp.
        """
        if self.clock_out_time and self.shift:
            shift_start_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))

            clock_in_time = max(self.clock_in_time, shift_start_datetime)
            clock_out_time = self.clock_out_time

            # Regular working hours
            regular_hours = shift_end_datetime - shift_start_datetime
            worked_time = clock_out_time - clock_in_time

            overtime = worked_time - regular_hours
            return max(round(overtime.total_seconds() / 3600, 2), 0)  # Make sure it's non-negative
        return 0

    def calculate_early_leave(self):
        """
        Calculates the early leave hours for this timestamp.
        """
        if self.clock_out_time and self.shift:
            shift_end_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))
            clock_out_time = self.clock_out_time

            # Early leave calculation
            if clock_out_time < shift_end_datetime:
                early_leave = shift_end_datetime - clock_out_time
                return max(round(early_leave.total_seconds() / 3600, 2), 0)  # Make sure it's non-negative
            return 0
        return 0

    def calculate_late_arrival(self):
        """
        Calculates the late arrival hours for this timestamp.
        """
        if self.clock_in_time and self.shift:
            shift_start_datetime = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
            clock_in_time = self.clock_in_time

            # Late arrival calculation
            if clock_in_time > shift_start_datetime:
                late_arrival = clock_in_time - shift_start_datetime
                return max(round(late_arrival.total_seconds() / 3600, 2), 0)  # Make sure it's non-negative
            return 0
        return 0

    @classmethod
    def get_monthly_summary(cls, user, month_start, today):
        """
        Calculates total worked hours, overtime, early leave, and late arrival for a user in a given month.
        """
        timestamps = cls.objects.filter(user=user, clock_in_time__date__gte=month_start, clock_in_time__date__lte=today)

        total_worked_hours = 0
        total_overtime_hours = 0
        total_early_leave_hours = 0
        total_late_arrival_hours = 0

        for timestamp in timestamps:
            total_worked_hours += timestamp.calculate_worked_hours()
            total_overtime_hours += timestamp.calculate_overtime()
            total_early_leave_hours += timestamp.calculate_early_leave()
            total_late_arrival_hours += timestamp.calculate_late_arrival()

        return {
            'total_worked_hours': total_worked_hours,
            'total_overtime_hours': total_overtime_hours,
            'total_early_leave_hours': total_early_leave_hours,
            'total_late_arrival_hours': total_late_arrival_hours
        }

    def __str__(self):
        return f"{self.user.name} - {self.clock_in_time} to {self.clock_out_time if self.clock_out_time else '未退勤'}"