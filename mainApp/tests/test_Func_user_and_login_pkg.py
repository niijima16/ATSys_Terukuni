# mainApp/tests/P_user_and_login_test.py
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
        テスト用のユーザーを作成し、ログイン状態にする共通のセットアップ処理。
        """
        # User_Masterモデルのユーザー作成
        self.user = User_Master.objects.create(
            account_id='test01@test.com',  # ログイン用のID
            password=hashlib.sha256('asdqwe'.encode()).hexdigest(),  # ハッシュ化されたパスワード
            name='Test User',
            age=30,
            gender='M',
            phone_number='1234567890',
            joined='2023-01-01',
            department_name='開発部',
            position='社員',
            employee_number=1  # ユーザーIDを1に設定
        )

        self.login_and_access_upload_shifts()

    def login_and_access_upload_shifts(self):
        """
        homePageからログインしてtopPageに遷移し、upload_shiftsページにアクセスする。
        """
        # ハッシュ化したパスワードでログイン
        login_url = reverse('homePage')
        hashed_password = hashlib.sha256('asdqwe'.encode()).hexdigest()
        self.client.post(login_url, {
            'account_id': 'test01@test.com',
            'password': hashed_password
        })

        # セッションにemployee_numberを設定
        session = self.client.session
        session['employee_number'] = self.user.employee_number
        session.save()
