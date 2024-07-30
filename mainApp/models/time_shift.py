from django.db import models
from .user_master import User_Master
from django.utils import timezone

class Shift(models.Model):
    user = models.ForeignKey(User_Master, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    start_time = models.TimeField()
    end_time = models.TimeField()
    break_time = models.DurationField(default='00:00:00')
    shift_type = models.CharField(max_length=50, blank=True)

    class Meta:
        unique_together = ('user', 'date')
        verbose_name = 'シフト'
        verbose_name_plural = 'シフト'

    def __str__(self):
        return f"{self.user.name} - {self.date} - {self.start_time} to {self.end_time}"