from django.urls import reverse
from .test_Func_user_and_login_pkg import BaseTestCase

class EditTimestampFunctionalityTests(BaseTestCase):
    """
    edit_timestamp/ページの機能を詳細に検証するテストケース。
    """

    def setUp(self):
        super().setUp()
        self.employee_user = self.user  # BaseTestCase の社員ユーザー
        self.manager_user = self.manager  # BaseTestCase のマネージャーユーザー
        self.employee_user.refresh_from_db()
        self.manager_user.refresh_from_db()
        self.employee = self.employee_user
        self.manager = self.manager_user

    def test_update_timestamp_information_success(self):
        """
        正しいデータで勤怠情報を更新できることを確認する。
        """
        self.client.session['employee_number'] = self.manager.employee_number
        self.client.session['target_employee_number'] = self.employee.employee_number
        self.client.session.save()

        update_data = {
            'clock_in': '09:00',
            'clock_out': '18:00',
        }
        response = self.client.post(reverse('edit_timestamp'), data=update_data)

        # データ更新確認
        self.assertEqual(response.status_code, 302)  # 更新後リダイレクトされること
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.timestamp.clock_in, update_data['clock_in'])
        self.assertEqual(self.employee.timestamp.clock_out, update_data['clock_out'])

    def test_update_timestamp_invalid_data(self):
        """
        不正なデータで勤怠情報を更新し、エラーメッセージが表示されることを確認する。
        """
        self.client.session['employee_number'] = self.manager.employee_number
        self.client.session['target_employee_number'] = self.employee.employee_number
        self.client.session.save()

        invalid_data = {
            'clock_in': 'invalid_time',  # 不正な時間フォーマット
            'clock_out': '',  # 空欄
        }
        response = self.client.post(reverse('edit_timestamp'), data=invalid_data)

        self.assertEqual(response.status_code, 200)  # ページが再表示されること
        self.assertContains(response, "有効な時刻を入力してください。")  # エラーメッセージ確認

    def test_edit_permission_denied_for_employee(self):
        """
        社員が他の社員の勤怠情報を編集しようとした場合のアクセス拒否を確認する。
        """
        self.client.session['employee_number'] = self.employee.employee_number
        self.client.session['target_employee_number'] = self.manager.employee_number
        self.client.session.save()

        response = self.client.get(reverse('edit_timestamp'))

        self.assertEqual(response.status_code, 403)  # 権限がないため403エラー

    def test_edit_permission_granted_for_manager(self):
        """
        マネージャーが他の社員の勤怠情報を編集できることを確認する。
        """
        self.client.session['employee_number'] = self.manager.employee_number
        self.client.session['target_employee_number'] = self.employee.employee_number
        self.client.session.save()

        response = self.client.get(reverse('edit_timestamp'))

        self.assertEqual(response.status_code, 200)  # アクセス成功
        self.assertContains(response, "勤怠情報編集")
