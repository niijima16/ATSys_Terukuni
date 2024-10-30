from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.messages import get_messages
from mainApp.models import User_Master
from django.http import HttpResponseForbidden

class TestShiftViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse("upload_shifts")

        # リーダーユーザーの作成
        self.leader = User_Master.objects.create(
            employee_number="10000001",
            account_id="leader_user",  # Ensure unique account_id
            name="Leader User",
            password="password",
            joined="2022-01-01",
            department_name="開発",
            position="リーダー",
            age=30
        )

        # 一般社員ユーザーの作成
        self.employee = User_Master.objects.create(
            employee_number="10000002",
            account_id="employee_user",  # Ensure unique account_id
            name="Employee User",
            password="password",
            joined="2022-01-01",
            department_name="開発",
            position="社員",
            age=25
        )

    def _setup_session(self, request, employee_number):
        """セッションのセットアップ"""
        from django.contrib.sessions.middleware import SessionMiddleware
        middleware = SessionMiddleware(lambda x: x)
        middleware.process_request(request)
        request.session['employee_number'] = employee_number
        request.session.save()

    def test_upload_shifts_authorized(self):
        """リーダーがシフトを正常にアップロードできることを確認する"""
        self.client.force_login(self.leader)
        with open('sample.csv', 'rb') as csv_file:
            response = self.client.post(self.upload_url, {'csv_file': csv_file})
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("シフトがアップロードされました" in str(message) for message in messages))

    def test_upload_shifts_unauthorized(self):
        """一般社員がシフトアップロードにアクセスできないことを確認する"""
        self.client.force_login(self.employee)
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 403)
