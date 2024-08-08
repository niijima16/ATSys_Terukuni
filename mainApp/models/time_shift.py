from django.db import models
from .user_master import User_Master
from django.utils import timezone
import calendar

class Shift(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_time = models.DurationField(default='00:00:00')
    shift_type = models.CharField(max_length=50, blank=True)
    weekday = models.CharField(max_length=9, default='Unknown', editable=False)
    is_weekend = models.BooleanField(default=False, editable=False)  # 土日を示すフィールド

    class Meta:
        unique_together = ('user', 'date')
        verbose_name = 'シフト'
        verbose_name_plural = 'シフト'

    def save(self, *args, **kwargs):
        # 曜日を設定
        weekday_index = self.date.weekday()
        self.weekday = calendar.day_name[weekday_index]
        self.is_weekend = weekday_index >= 5  # 土曜日（5）または日曜日（6）の場合はTrue
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.name} - {self.date} ({self.weekday}) - {self.start_time} to {self.end_time}"