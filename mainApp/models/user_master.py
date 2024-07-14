'''
外部キー引用リスト
1.COMPANY
2.
3.
'''

from django.db import models

class User_Master(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False) # 一意､プライマリーキー
    account_id = models.EmailField(max_length=255, unique=True) # @levels.co.jp判断はフロント側でやる
    password = models.CharField(max_length=255) # パスワード
    name = models.CharField(max_length=255) # 名前
    age = models.PositiveSmallIntegerField() # 年齢を示すフィールド
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES) # 性別略
    phone_number = models.CharField(max_length=11) # 電話番号を示すフィールド
    joined = models.DateField() # 入社日
    department_name = models.CharField(max_length=255) # 部門名称
    position = models.CharField(max_length=255, default='正社員') #役職
    company = models.ForeignKey('COMPANY', on_delete=models.CASCADE) # 外部キー､「COMPANY」テーブルを呼び出すため

    def save(self, *args, **kwargs):
        # パスワードをハッシュ化しない
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name