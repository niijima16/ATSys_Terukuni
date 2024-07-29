from django.db import models

class User_Master(models.Model):
    user_id = models.PositiveIntegerField(primary_key=True, unique=True, editable=False)
    account_id = models.EmailField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    age = models.PositiveSmallIntegerField()
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=11)
    joined = models.DateField()
    department_name = models.CharField(max_length=255)

    POSITION_CHOICES = [
        ('社員', '平社員'),
        ('リーダー', 'リーダー'),
        ('マネージャー', 'マネージャー'),
        ('課長', '課長'),
        ('部長', '部長'),
        ('取締役', '取締役'),
        ('社長', '社長'),
    ]
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='社員')
    company = models.ForeignKey('COMPANY', on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        if not self.user_id:
            # 新規作成時にuser_idが設定されていない場合に自動的に設定する
            last_user = User_Master.objects.order_by('user_id').last()
            self.user_id = last_user.user_id + 1 if last_user else 1
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name