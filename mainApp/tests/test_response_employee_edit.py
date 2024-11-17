from django.urls import reverse
from mainApp.models import User_Master
from .test_Func_user_and_login_pkg import BaseTestCase

class EditEmployeeFunctionalityTests(BaseTestCase):
    """
    edit_employee/ページの機能を詳細に検証するテストケース。
    """

    def setUp(self):
        super().setUp()
        self.employee_user = self.user  # BaseTestCase の社員ユーザー
        self.manager_user = self.manager  # BaseTestCase のマネージャーユーザー
        self.employee_user.refresh_from_db()
        self.manager_user.refresh_from_db()
        self.employee = self.employee_user  # 社員のユーザーを設定
        self.manager = self.manager_user  # マネージャーのユーザーを設定

    def test_update_employee_information_success(self):
        """
        正しいデータで社員情報を更新できることを確認する。
        """
        self.client.session['employee_number'] = self.manager.employee_number
        self.client.session.save()

        update_data = {
            'name': 'Updated Name',
            'age': 30,
            'gender': 'F',
            'phone_number': '09087654321',
            'department_name': '総務部',
            'position': '課長'
        }
        response = self.client.post(reverse('edit_employee', kwargs={'employee_number': self.employee.employee_number}), data=update_data)

        self.employee.refresh_from_db()
        self.assertEqual(self.employee.name, update_data['name'])
        self.assertEqual(self.employee.age, update_data['age'])
        self.assertEqual(self.employee.phone_number, update_data['phone_number'])
        self.assertEqual(self.employee.department_name, update_data['department_name'])
        self.assertEqual(self.employee.position, update_data['position'])
        self.assertRedirects(response, reverse('edit_employee', kwargs={'employee_number': self.employee.employee_number}))

    def test_update_employee_invalid_data(self):
        """
        不正なデータで社員情報を更新し、エラーメッセージが表示されることを確認する。
        """
        self.client.session['employee_number'] = self.manager.employee_number
        self.client.session.save()

        invalid_data = {
            'name': '',  # 名前が空欄
            'age': -1,  # 年齢が不正
        }
        response = self.client.post(reverse('edit_employee', kwargs={'employee_number': self.employee.employee_number}), data=invalid_data)

        self.assertContains(response, "このフィールドは必須です。")
        self.assertContains(response, "0以上の数値を入力してください。")

    def test_edit_permission_denied_for_employee(self):
        """
        社員が他の社員の情報を編集しようとした場合のアクセス拒否を確認する。
        """
        self.client.session['employee_number'] = self.employee.employee_number
        self.client.session.save()

        response = self.client.get(reverse('edit_employee', kwargs={'employee_number': self.manager.employee_number}))

        self.assertEqual(response.status_code, 403)

    def test_edit_permission_granted_for_manager(self):
        """
        マネージャーが他の社員の情報を編集できることを確認する。
        """
        self.client.session['employee_number'] = self.manager.employee_number
        self.client.session.save()

        response = self.client.get(reverse('edit_employee', kwargs={'employee_number': self.employee.employee_number}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "社員情報編集")
