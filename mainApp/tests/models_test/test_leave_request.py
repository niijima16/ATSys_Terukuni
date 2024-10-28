from django.test import TestCase
from django.db import IntegrityError
from mainApp.models.leave_request import LeaveRequest
from mainApp.models.user_master import User_Master
from django.utils import timezone
from datetime import timedelta

class LeaveRequestModelTest(TestCase):
    def setUp(self):
        # テスト用のユーザーと上長を作成
        self.user = User_Master.objects.create(
            name="Applicant",
            account_id="applicant@example.com",
            age=30,
            gender="M",
            phone_number="09012345678",
            joined=timezone.now().date(),
            department_name="Test Department",
            position="社員"  # 修正: role ではなく position を使用
        )
        self.superior = User_Master.objects.create(
            name="Superior",
            account_id="superior@example.com",
            age=40,
            gender="M",
            phone_number="08012345679",
            joined=timezone.now().date(),
            department_name="Management",
            position="部長"  # 修正: 上長のポジション
        )

    def test_leave_request_creation(self):
        # LeaveRequestインスタンスが正しく作成されることをテストします。
        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type='Paid',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            applicant_comment='Vacation'
        )

        # 各フィールドが正しく保存されているかをアサート
        self.assertEqual(leave_request.user, self.user)
        self.assertEqual(leave_request.leave_type, 'Paid')
        self.assertEqual(leave_request.applicant_comment, 'Vacation')
        self.assertFalse(leave_request.approved)  # デフォルトで未承認

    def test_leave_request_string_representation(self):
        # LeaveRequestインスタンスの文字列表現が正しいことをテストします。
        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type='Paid',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            applicant_comment='Vacation'
        )

        # 期待される文字列表現と一致するかをアサート
        expected_str = f"{self.user.name} - {leave_request.get_leave_type_display()} ({leave_request.start_date} から {leave_request.end_date})"
        self.assertEqual(str(leave_request), expected_str)

    def test_approver_can_approve(self):
        # 承認者が申請を承認すると、承認者リストに追加されることをテストします。
        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type='Paid',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            applicant_comment='Vacation'
        )
        leave_request.approved_by.add(self.superior)
        leave_request.save()

        # 承認者リストに上長が含まれているかをアサート
        self.assertIn(self.superior, leave_request.approved_by.all())

    def test_approval_status_after_all_approvers_approve(self):
        # 承認者全員が承認した後、申請が承認済みになることをテストします。
        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type='Paid',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            applicant_comment='Vacation'
        )
        leave_request.approved_by.add(self.superior)
        leave_request.save()

        # 承認が正しく処理されていることを確認
        if leave_request.approved_by.count() == self.user.get_superiors().count():
            leave_request.approved = True
        self.assertTrue(leave_request.approved)

    def test_leave_request_with_multiple_approvers(self):
        # 複数の承認者が存在する場合の承認処理をテストします。
        another_superior = User_Master.objects.create(
            name="Another Superior",
            account_id="another_superior@example.com",
            age=45,
            gender="M",
            phone_number="07012345678",
            joined=timezone.now().date(),
            department_name="Management",
            position="部長"
        )

        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type='Paid',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            applicant_comment='Vacation'
        )
        leave_request.approved_by.add(self.superior, another_superior)
        leave_request.save()

        # 全ての承認者が承認していることを確認
        self.assertEqual(leave_request.approved_by.count(), 2)

    def test_approver_comment(self):
        # 承認者がコメントを追加できることをテストします。
        leave_request = LeaveRequest.objects.create(
            user=self.user,
            leave_type='Paid',
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=2),
            applicant_comment='Vacation'
        )
        leave_request.approver_comment = 'Approved by superior'
        leave_request.save()

        # 承認者のコメントが正しく保存されていることをアサート
        self.assertEqual(leave_request.approver_comment, 'Approved by superior')

