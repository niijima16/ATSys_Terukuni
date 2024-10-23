# models/paid_leave.py

from django.db import models
from .user_master import User_Master

class PaidLeave(models.Model):
    user = models.OneToOneField(User_Master, on_delete=models.CASCADE, related_name='paid_leave')
    total_days = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # 初期有給日数
    used_days = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # 使用済み有給日数
    remaining_days = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # 残り有給日数

    def save(self, *args, **kwargs):
        # 残り有給日数を自動計算
        self.remaining_days = self.total_days - self.used_days
        super().save(*args, **kwargs)

    def use_leave(self, days):
        """
        指定した日数の有給を使用するメソッド。
        """
        if days <= self.remaining_days:
            self.used_days += days
            self.save()
        else:
            raise ValueError("指定された日数が残り有給日数を超えています。")

    def __str__(self):
        return f"{self.user.name} - 残り有給: {self.remaining_days}日"