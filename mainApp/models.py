from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


# Create your models here.
def validate_account_id(value):
    if not value.endswith('@levels.co.jp'):
        raise ValidationError('アカウントIDは@levels.co.jpで終わる必要があります。')

class user_master(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False) # 一意
    account_id = models.EmailField(max_length=256, unique=True, validators=[validate_account_id]) # @levels.co.jp判断つき
    password = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    age = models.PositiveSmallIntegerField()  # 年齢を示すフィールド
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=11)  # 電話番号を示すフィールド
    joined = models.DateField()
    department_id = models.PositiveIntegerField()
    department = models.CharField(max_length=256)

    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = user_master.objects.all().order_by('-user_id').first()
            if last_user:
                self.user_id = last_user.user_id + 1
            else:
                self.user_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
