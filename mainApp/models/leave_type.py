from django.db import models

class LeaveType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = '休暇タイプ'
        verbose_name_plural = '休暇タイプ'

    def __str__(self):
        return self.name