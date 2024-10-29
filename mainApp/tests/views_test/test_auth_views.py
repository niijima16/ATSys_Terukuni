from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User  # テストユーザー作成に必要

class AuthViewsTestCase(TestCase):
    """認証関連ビューの動作を検証するためのテストケース"""

    def test_login_view_get(self):
        """トップページ（ログイン画面）のGETリクエストが正常に表示されることを確認する"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)  # ステータスコード200を期待
        self.assertTemplateUsed(response, 'login.html')  # テンプレート確認


    def test_register_view_get(self):
        """登録ページのGETリクエストが正常に表示されることを確認する"""
        response = self.client.get(reverse('registerPage'))  # 'registerPage'にアクセス
        self.assertEqual(response.status_code, 200)

    def test_logout_view(self):
        """ログアウト後、トップページにリダイレクトされることを確認する"""
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('homePage'))  # リダイレクト先の修正


    def test_register_view_post_valid(self):
        """有効なデータを使って登録を行い、リダイレクトされることを確認する"""
        form_data = {
            'account_id': 'testuser@example.com',
            'password': 'testpass123',
            'name': 'Test User',
            'age': 30,
            'gender': 'M',
            'phone_number': '09012345678',
            'department_name': '営業部',
            'position': '社員',
        }
        response = self.client.post(reverse('registerPage'), data=form_data)
        self.assertEqual(response.status_code, 302)  # 成功時のリダイレクトを確認
        self.assertRedirects(response, reverse('homePage'))  # 期待するリダイレクト先


    def test_register_view_post_invalid_password(self):
        """不一致のパスワードで登録し、ページが再表示されることを確認する"""
        form_data = {'username': 'user1', 'password1': 'pass1234', 'password2': 'wrongpass'}
        response = self.client.post(reverse('registerPage'), data=form_data)
        self.assertEqual(response.status_code, 200)  # エラー時は再表示される

    def test_login_view_post_invalid(self):
        """無効なログイン情報を使い、エラーメッセージとともにページが再表示されることを確認する"""
        form_data = {'username': 'user1', 'password': 'wrongpass'}
        response = self.client.post(reverse('topPage'), data=form_data)
        self.assertEqual(response.status_code, 200)  # エラー時は再表示

    def test_login_view_post_valid(self):
        """有効なログイン情報を使い、リダイレクトされることを確認する"""
        # ユーザーを事前に作成（ログインに必要）
        User.objects.create_user(username='user1', password='pass1234')

        form_data = {'username': 'user1', 'password': 'pass1234'}
        response = self.client.post(reverse('topPage'), data=form_data)
        self.assertEqual(response.status_code, 302)  # 成功時のリダイレクトを確認
