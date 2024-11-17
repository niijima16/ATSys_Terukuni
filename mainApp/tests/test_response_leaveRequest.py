from django.urls import reverse
from mainApp.models import LeaveRequest
from .test_Func_user_and_login_pkg import BaseTestCase


class LeaveApprovalTests(BaseTestCase):
    """
    承認機能をテストするケース。
    """

    def setUp(self):
        super().setUp()
        # 休暇申請を作成（社員が申請）
        self.leave_request = LeaveRequest.objects.create(
            user=self.user,  # 社員が申請
            leave_type='Paid',
            start_date='2024-11-20',
            end_date='2024-11-22',
            is_paid_leave=True,
            applicant_comment="休暇を取得したいです。",
        )

    def test_manager_can_approve(self):
        """
        マネージャーが休暇申請を承認できることを確認する。
        """
        # マネージャーでログイン
        self.login_user(self.manager)

        approve_url = reverse('approve_leave', args=[self.leave_request.id])
        response = self.client.post(approve_url, {'approved': True})

        self.leave_request.refresh_from_db()
        self.assertTrue(self.leave_request.approved)  # 承認されたことを確認
        self.assertRedirects(response, reverse('approve_leave', args=[self.leave_request.id]))

    def test_employee_cannot_approve(self):
        """
        一般社員が休暇申請を承認できないことを確認する。
        """
        approve_url = reverse('approve_leave', args=[self.leave_request.id])
        response = self.client.post(approve_url, {'approved': True})

        self.leave_request.refresh_from_db()
        self.assertFalse(self.leave_request.approved)  # 承認されていないことを確認
        self.assertEqual(response.status_code, 403)  # 権限不足で403が返ることを確認
