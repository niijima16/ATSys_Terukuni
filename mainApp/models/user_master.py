from django.db import models
from django.core.exceptions import ValidationError
from .company import COMPANY
'''
外部キー引用リスト
1.Company
2.
3.
'''

# Custom validator for account_id (assuming it checks for the @levels.co.jp domain)
def validate_account_id(value):
    if not value.endswith('@levels.co.jp'):
        raise ValidationError('Email must be with the @levels.co.jp domain')

class User_Master(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False)  # 一意､プライマリーキー
    account_id = models.EmailField(max_length=255, unique=True, validators=[validate_account_id])  # @levels.co.jp判断つき
    password = models.CharField(max_length=255)  # パスワード
    name = models.CharField(max_length=255)  # 名前
    age = models.PositiveSmallIntegerField()  # 年齢を示すフィールド
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)  # 性別略
    phone_number = models.CharField(max_length=11)  # 電話番号を示すフィールド
    joined = models.DateField()  # 入社日
    department = models.ForeignKey(COMPANY, on_delete=models.CASCADE, db_column='department_id')  # 部門番号（外部キー）
    department_name = models.CharField(max_length=255)  # 部門名称
    position = models.CharField(max_length=255, default='正社員')


    def save(self, *args, **kwargs):
        if not self.user_id:
            last_user = User_Master.objects.all().order_by('-user_id').first()
            if last_user:
                self.user_id = last_user.user_id + 1
            else:
                self.user_id = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
