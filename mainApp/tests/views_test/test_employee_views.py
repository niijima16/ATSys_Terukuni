from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.auth.hashers import make_password
from mainApp.models import User_Master
from mainApp.forms import RegisterForm, EmployeeEditForm
from mainApp.views.employee_views import registerPage, edit_employee

class TestEmployeeViews(TestCase):
    """employee_views.py のビューをテストするクラス"""

    def setUp(self):
        """テスト用の初期設定"""
        self.factory = RequestFactory()

        # テスト用のユーザー（マネージャー）を作成
        self.manager = User_Master.objects.create(
            account_id='manager@example.com',
            password=make_password('password123'),  # パスワードはハッシュ化
            name='Manager User',
            age=35,
            gender='M',
            phone_number='08012345678',
            joined='2023-01-01',
            department_name='営業部',
            position='マネージャー'
        )

        # テスト用の編集対象社員を作成
        self.employee = User_Master.objects.create(
            account_id='employee@example.com',
            password=make_password('password123'),
            name='Employee User',
            age=28,
            gender='M',
            phone_number='08087654321',
            joined='2023-01-01',
            department_name='開発部',
            position='社員'
        )

    def _setup_request(self, request):
        """リクエストにセッションとメッセージを設定"""
        session_middleware = SessionMiddleware(lambda req: None)
        session_middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

    def test_registerPage_success(self):
        """POSTリクエストでユーザーが正常に登録され、リダイレクトされることを確認する"""
        request = self.factory.post('/register/', {
            'account_id': 'newuser@example.com',
            'password': 'password123',
            'name': 'New User',
            'age': 25,
            'gender': 'M',
            'phone_number': '08098765432',
            'joined': '2024-01-01',
            'department_name': '営業部',
            'position': '社員'
        })
        self._setup_request(request)

        response = registerPage(request)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('homePage'))

    def test_registerPage_invalid_form(self):
        """無効なデータでPOSTリクエストした場合、登録ページに留まることを確認する"""
        request = self.factory.post('/register/', {
            'account_id': 'invalid-email',  # 無効なメール形式
            'password': 'password123',
            'name': '',
        })
        self._setup_request(request)

        response = registerPage(request)
        self.assertEqual(response.status_code, 200)  # ページに留まることを確認

    def test_edit_employee_success(self):
        """POSTリクエストで社員情報が正常に更新され、リダイレクトされることを確認する"""
        # POSTリクエストに必要な全てのデータを含める
        request = self.factory.post('/edit/', {
            'account_id': 'updated_employee@example.com',  # 必須フィールドを追加
            'name': 'Updated Employee',
            'age': 30,
            'phone_number': '08099999999',
            'gender': 'M',
            'joined': '2023-01-01',
            'department_name': '開発部',
            'position': '社員',
        })
        self._setup_request(request)
        request.session['employee_number'] = self.manager.employee_number  # マネージャーとしてログイン

        request.GET = {'employee_number': self.employee.employee_number}  # 編集対象の社員番号を指定

        response = edit_employee(request)

        # ステータスコード302でリダイレクトされたことを確認
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('topPage'))




    def test_edit_employee_no_employee_number(self):
        """社員番号が指定されていない場合、エラーメッセージを表示することを確認する"""
        request = self.factory.get('/edit/')
        self._setup_request(request)
        request.session['employee_number'] = self.manager.employee_number

        response = edit_employee(request)
        self.assertEqual(response.status_code, 200)
        # UTF-8 エンコードされた文字列でエラーメッセージを確認
        self.assertIn("社員番号が指定されていません。", response.content.decode('utf-8'))

    def test_edit_employee_employee_not_found(self):
        """存在しない社員番号が指定された場合、エラーメッセージを表示することを確認する"""
        request = self.factory.get('/edit/?employee_number=99999999')  # 存在しない社員番号
        self._setup_request(request)
        request.session['employee_number'] = self.manager.employee_number

        response = edit_employee(request)
        self.assertEqual(response.status_code, 200)
        # UTF-8 エンコードされた文字列でエラーメッセージを確認
        self.assertIn("該当する社員が見つかりません。", response.content.decode('utf-8'))

