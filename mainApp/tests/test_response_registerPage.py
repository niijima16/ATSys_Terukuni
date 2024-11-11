from .test_Func_user_and_login_pkg import BaseTestCase
from django.urls import reverse
from mainApp.models import User_Master

class RegisterPageTests(BaseTestCase):
    """
    登録ページのレスポンスやテンプレートを検証するテストケース。
    """

    def test_register_page_status_code(self):
        """
        registerPageが正常に200ステータスコードを返すかを確認するテスト。
        """
        # registerPageにアクセス
        response = self.client.get(reverse('registerPage'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_template_used(self):
        """
        registerPageが正しいテンプレート('Registration.html')を使用しているかを確認するテスト。
        """
        # registerPageにアクセス
        response = self.client.get(reverse('registerPage'))
        self.assertTemplateUsed(response, 'Registration.html')

    def test_register_page_content(self):
        """
        registerPageにUser_Masterの内容が含まれているかを確認するテスト。
        """
        # registerPageにアクセス
        response = self.client.get(reverse('registerPage'))
        
        # ページに表示される各フィールドの確認
        self.assertContains(response, "ユーザー登録")
        self.assertContains(response, "登録")
        self.assertContains(response, "Account id")
        self.assertContains(response, "Password")
        self.assertContains(response, "Name")
        self.assertContains(response, "Age")
        self.assertContains(response, "Gender")
        self.assertContains(response, "Phone number")
        self.assertContains(response, "Joined")
        self.assertContains(response, "Department name")
        self.assertContains(response, "Position")
