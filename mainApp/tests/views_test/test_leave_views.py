from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sessions.middleware import SessionMiddleware
from django.contrib.messages.middleware import MessageMiddleware
from mainApp.models import User_Master, PaidLeave
from mainApp.views.leave_views import apply_leave, leave_requests

class TestLeaveViews(TestCase):
    """leave_views.py のビューをテストするクラス"""

    def setUp(self):
        """テスト用の初期設定"""
        self.factory = RequestFactory()

        # マネージャーと社員のテストユーザー作成
        self.manager = User_Master.objects.create(
            account_id='manager@example.com',
            password='password123',
            name='Manager User',
            position='マネージャー',
            employee_number=10000000,
            age=40,
            gender='M',
            phone_number='08012345678',
            department_name='営業部',
            joined='2020-01-01'
        )

        self.employee = User_Master.objects.create(
            account_id='employee@example.com',
            password='password123',
            name='Employee User',
            position='社員',
            employee_number=10000001,
            age=30,
            gender='M',
            phone_number='08087654321',
            department_name='開発部',
            joined='2021-06-01'
        )

        # 有給日数を十分に設定
        self.paid_leave = PaidLeave.objects.create(
            user=self.employee,
            remaining_days=10  # 必要な日数以上を設定
        )

    def _setup_request(self, request):
        """リクエストにセッションとメッセージをセットアップする"""
        middleware = SessionMiddleware(lambda req: None)
        middleware.process_request(request)
        request.session.save()

        message_middleware = MessageMiddleware(lambda req: None)
        message_middleware.process_request(request)

    def test_apply_leave_success(self):
        """正常な有給申請が成功することを確認する"""
        request = self.factory.post('/apply_leave/', {
            'start_date': '2024-11-01',
            'end_date': '2024-11-02',  # 2日間の申請
            'leave_type': 'Paid',
            'applicant_comment': '休暇をお願いします。'
        })
        self._setup_request(request)
        request.session['employee_number'] = self.employee.employee_number

        response = apply_leave(request)

        # デバッグ: レスポンスの内容を確認
        if response.status_code == 200:
            print("フォームエラー:", response.content.decode('utf-8'))

        # ステータスコードの確認
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('topPage'))

    def test_leave_requests_success(self):
        """リーダー以上の役職が申請一覧にアクセスできることを確認する"""
        request = self.factory.get('/leave_requests/')
        self._setup_request(request)
        request.session['employee_number'] = self.manager.employee_number

        response = leave_requests(request)

        # ステータスコードの確認
        self.assertEqual(response.status_code, 200)
        self.assertIn("未承認の申請", response.content.decode('utf-8'))
