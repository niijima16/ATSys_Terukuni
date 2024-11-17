from django.test import TestCase
from django.urls import reverse
from mainApp.models import User_Master
import hashlib


class BaseTestCase(TestCase):
    """
    共通のセットアップ処理を持つテストケースのベースクラス。
    """

    def setUp(self):
        """
        テスト用の一般ユーザー（社員）とマネージャーを作成し、ログイン状態にする。
        """
        # 社員（一般ユーザー）の作成
        self.user = User_Master.objects.create(
            account_id='employee@test.com',
            password=hashlib.sha256('employee123'.encode()).hexdigest(),
            name='Employee User',
            age=30,
            gender='M',
            phone_number='1234567890',
            joined='2022-01-01',
            department_name='開発部',
            position='社員',
            employee_number=10000001,
        )

        # マネージャーの作成
        self.manager = User_Master.objects.create(
            account_id='manager@test.com',
            password=hashlib.sha256('manager123'.encode()).hexdigest(),
            name='Manager User',
            age=40,
            gender='F',
            phone_number='0987654321',
            joined='2020-01-01',
            department_name='開発部',
            position='マネージャー',
            employee_number=10000002,
        )

        # デフォルトで社員をログイン状態に設定
        self.login_user(self.user)

    def login_user(self, user):
        """
        指定されたユーザーでログインし、セッションを設定する。
        """
        login_url = reverse('homePage')
        hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
        self.client.post(login_url, {'account_id': user.account_id, 'password': hashed_password})
        session = self.client.session
        session['employee_number'] = user.employee_number
        session.save()
