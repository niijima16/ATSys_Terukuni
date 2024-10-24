# time_shift.py

from django.db import models
from .user_master import User_Master
from django.utils import timezone
import calendar
from datetime import timedelta

class Shift(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField(null=True, blank=True)  # 空欄を許可
    end_time = models.TimeField(null=True, blank=True)  # 空欄を許可
    break_time = models.DurationField(default=timedelta(hours=0))  # デフォルト値として0時間を設定
    shift_type = models.CharField(max_length=50, blank=True)
    weekday = models.CharField(max_length=9, default='Unknown', editable=False)
    is_weekend = models.BooleanField(default=False, editable=False)  # 土日を示すフィールド
    is_off_day = models.BooleanField(default=False, editable=False)  # 休みの日を示すフィールド

    class Meta:
        unique_together = ('user', 'date')
        verbose_name = 'シフト'
        verbose_name_plural = 'シフト'

    def save(self, *args, **kwargs):
        # 曜日を設定
        weekday_index = self.date.weekday()
        self.weekday = calendar.day_name[weekday_index]  # 英語で曜日名を取得
        self.is_weekend = weekday_index >= 5  # 土曜日（5）または日曜日（6）の場合はTrue
        
        # 開始時間と終了時間が空の場合は休みの日としてマーク
        self.is_off_day = self.start_time is None and self.end_time is None

        super().save(*args, **kwargs)

    def __str__(self):
        start = self.start_time.strftime('%H:%M') if self.start_time else '休み'
        end = self.end_time.strftime('%H:%M') if self.end_time else '休み'
        return f"{self.user.employee_number} - {self.date} ({self.weekday}) - {start} to {end}"