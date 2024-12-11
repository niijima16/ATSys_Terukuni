# time_shift.py

# from django.db import models
# from .user_master import User_Master
# from django.utils import timezone
# import calendar
# from datetime import timedelta

# class Shift(models.Model):
#     user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
#     date = models.DateField(default=timezone.now)
#     start_time = models.TimeField(null=True, blank=True)  # 空欄を許可
#     end_time = models.TimeField(null=True, blank=True)  # 空欄を許可
#     break_time = models.DurationField(default=timedelta(hours=0))  # デフォルト値として0時間を設定
#     shift_type = models.CharField(max_length=50, blank=True)
#     weekday = models.CharField(max_length=9, default='Unknown', editable=False)
#     is_weekend = models.BooleanField(default=False, editable=False)  # 土日を示すフィールド
#     is_off_day = models.BooleanField(default=False, editable=False)  # 休みの日を示すフィールド

#     class Meta:
#         unique_together = ('user', 'date')
#         verbose_name = 'シフト'
#         verbose_name_plural = 'シフト'

#     def save(self, *args, **kwargs):
#         # 曜日を設定
#         weekday_index = self.date.weekday()
#         self.weekday = calendar.day_name[weekday_index]  # 英語で曜日名を取得
#         self.is_weekend = weekday_index >= 5  # 土曜日（5）または日曜日（6）の場合はTrue
        
#         # 開始時間と終了時間が空の場合は休みの日としてマーク
#         self.is_off_day = self.start_time is None and self.end_time is None

#         super().save(*args, **kwargs)

#     def __str__(self):
#         start = self.start_time.strftime('%H:%M') if self.start_time else '休み'
#         end = self.end_time.strftime('%H:%M') if self.end_time else '休み'
#         return f"{self.user.employee_number} - {self.date} ({self.weekday}) - {start} to {end}"

from django.db import models
from datetime import timedelta

class Shift(models.Model):
    user = models.ForeignKey('User_Master', on_delete=models.CASCADE, related_name="shifts")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    break_time = models.DurationField(null=True, blank=True, default=timedelta(hours=1))  # デフォルト1時間
    is_weekend = models.BooleanField(default=False)  # 週末かどうかを示すフィールド

    def save(self, *args, **kwargs):
        """
        saveメソッドで週末かどうかを自動判定し、is_weekendフィールドを更新。
        """
        # 曜日が土日ならTrue (0=月曜日, ..., 6=日曜日)
        self.is_weekend = self.date.weekday() >= 5  
        super().save(*args, **kwargs)

    def __str__(self):
        """
        管理画面やデバッグ時に役立つ文字列表現。
        """
        if self.is_weekend:
            return f"{self.user.name} - {self.date} (週末)"
        return f"{self.user.name} - {self.date} ({self.start_time} - {self.end_time})"

    class Meta:
        """
        メタ情報: モデルの順序や表名を設定。
        """
        ordering = ['date']
        verbose_name = "シフト"
        verbose_name_plural = "シフト"

