# user_master.py

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
        ('社員', '社員'),
        ('リーダー', 'リーダー'),
        ('マネージャー', 'マネージャー'),
        ('課長', '課長'),
        ('部長', '部長'),
        ('取締役', '取締役'),
        ('社長', '社長'),
    ]
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='社員')
    employee_number = models.PositiveIntegerField(unique=True, editable=False)
    
    def get_superiors(self):
        """
        このユーザーの上長を取得するヘルパーメソッド。
        取締役と社長は除外します。
        """
        positions_order = ['社員', 'リーダー', 'マネージャー', '課長', '部長']
        user_position_index = positions_order.index(self.position)
        # ユーザーより上の役職に属する全てのユーザーを取得
        superiors = User_Master.objects.filter(position__in=positions_order[user_position_index + 1:])
        return superiors

    def save(self, *args, **kwargs):
        if not self.user_id:
            # 新規作成時にuser_idが設定されていない場合に自動的に設定する
            last_user = User_Master.objects.order_by('user_id').last()
            self.user_id = last_user.user_id + 1 if last_user else 1

        if not self.employee_number:
            # 最新の社員番号を取得し、1を追加
            last_employee = User_Master.objects.order_by('employee_number').last()
            if last_employee:
                self.employee_number = last_employee.employee_number + 1
            else:
                self.employee_number = 10000000

        # フロントエンドで暗号化済みのため、ここでのハッシュ化は不要
        super().save(*args, **kwargs)

    def get_superiors(self):
        """
        自分より上の役職のユーザーを返すメソッド。
        承認権限のあるユーザーを返します。
        """
        superior_positions = ['社員', 'リーダー', 'マネージャー', '課長', '部長']
        position_hierarchy = {
            '社員': ['リーダー', 'マネージャー', '課長', '部長', '取締役', '社長'],
            'リーダー': ['マネージャー', '課長', '部長', '取締役', '社長'],
            'マネージャー': ['課長', '部長', '取締役', '社長'],
            '課長': ['部長', '取締役', '社長'],
            '部長': ['取締役', '社長'],
        }

        # 自分の役職のリストに基づいて承認権限のある役職のユーザーを取得
        if self.position in position_hierarchy:
            return User_Master.objects.filter(position__in=position_hierarchy[self.position])
        return User_Master.objects.none()

    def __str__(self):
        return f"{self.name} - {self.employee_number}"
