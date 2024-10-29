from django.test import TestCase
from django.urls import reverse
from mainApp.models import User_Master, TimeStamp
from datetime import date

class EditTimestampUnitTest(TestCase):
    """edit_timestamp関数の単体テスト"""

    def setUp(self):
        """テスト用のデータをセットアップ"""
        # マネージャーユーザーを作成
        self.manager = User_Master.objects.create(
            user_id=1,
            account_id='manager@example.com',
            password='managerpass',
            name='Manager User',
            age=45,
            gender='M',
            phone_number='09012345678',
            joined=date(2020, 1, 1),
            department_name='管理部',
            position='マネージャー',
            employee_number=12345
        )

        # 一般社員を作成
        self.employee = User_Master.objects.create(
            user_id=2,
            account_id='employee@example.com',
            password='employeepass',
            name='Employee User',
            age=30,
            gender='F',
            phone_number='09087654321',
            joined=date(2021, 6, 15),
            department_name='営業部',
            position='社員',
            employee_number=67890
        )

        # ログイン状態のシミュレーション
        session = self.client.session
        session['employee_number'] = 12345  # マネージャーとして認証
        session.save()

    def test_edit_own_timestamp(self):
        """管理者が自分自身の勤怠情報を編集する場合"""
        response = self.client.get(reverse('edit_timestamp'), {'employee_number': '12345'})

        # ステータスコードとテンプレートの確認
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_timestamp.html')

        # コンテキストの確認
        context = response.context
        self.assertIn('employee', context)
        self.assertTrue(context['is_self'])

    def test_edit_other_employee_timestamp(self):
        """管理者が他の社員の勤怠情報を編集する場合"""
        response = self.client.get(reverse('edit_timestamp'), {'employee_number': '67890'})

        # ステータスコードとテンプレートの確認
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'edit_timestamp.html')

        # コンテキストの確認
        context = response.context
        self.assertIn('employee', context)
        self.assertFalse(context['is_self'])

    def test_permission_denied_for_non_manager(self):
        """マネージャー権限がない場合、PermissionDeniedが発生することを確認"""
        # セッションを一般社員のものに変更
        session = self.client.session
        session['employee_number'] = 67890  # 一般社員として認証
        session.save()

        response = self.client.get(reverse('edit_timestamp'), {'employee_number': '12345'})

        # 権限がない場合、403 Forbiddenが返されることを確認
        self.assertEqual(response.status_code, 403)

