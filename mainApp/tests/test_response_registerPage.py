from django.test import TestCase
from django.urls import reverse
from mainApp.models import User_Master
import hashlib

class RegisterPageTests(TestCase):
    """
    登録ページのレスポンスやテンプレートを検証するテストケース。
    """

    def setUp(self):
        """
        テストの準備としてカスタマイズしたユーザーを作成し、ログインを行う。
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
            position='社員'
        )

    def login_and_access_register_page(self):
        """
        ログイン後、homePageからregisterPageへの遷移を確認する。
        """
        # ハッシュ化したパスワードでログイン
        login_url = reverse('homePage')
        hashed_password = hashlib.sha256('asdqwe'.encode()).hexdigest()
        self.client.post(login_url, {
            'account_id': 'test01@test.com',
            'password': hashed_password
        })

        # homePageからregisterPageに遷移
        response = self.client.get(reverse('registerPage'))
        return response

    def test_register_page_status_code(self):
        """
        registerPageが正常に200ステータスコードを返すかを確認するテスト。
        """
        response = self.login_and_access_register_page()
        self.assertEqual(response.status_code, 200)

    def test_register_page_template_used(self):
        """
        registerPageが正しいテンプレート('registerPage.html')を使用しているかを確認するテスト。
        """
        response = self.login_and_access_register_page()
        self.assertTemplateUsed(response, 'registerPage.html')

    def test_register_page_content(self):
        """
        registerPageに必要なコンテンツが含まれているかを確認するテスト。
        """
        response = self.login_and_access_register_page()
        self.assertContains(response, "新規社員アカウント登録")
        self.assertContains(response, "登録")
