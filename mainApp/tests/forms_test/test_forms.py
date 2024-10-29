from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from mainApp.forms import (
    RegisterForm, LoginForm, ShiftUploadForm, LeaveRequestForm, ApproveLeaveForm, EmployeeEditForm, TimeStampEditForm
)
from mainApp.models import User_Master, LeaveRequest, TimeStamp
from io import BytesIO

class FormsTestCase(TestCase):
    # セットアップメソッド：テスト用の初期ユーザーインスタンスを作成
    def setUp(self):
        self.user = User_Master.objects.create(
            account_id='testuser@example.com',
            password='SecurePassword123!',
            name='Test User',
            age=30,
            gender='M',
            phone_number='1234567890',
            joined=timezone.now().date(),
            department_name='Test Department',
            position='社員'
        )
        
    # 登録フォームが有効なデータを受け入れるか確認するテスト
    def test_register_form_valid(self):
        form_data = {
            'account_id': 'newuser@example.com',  # 有効なメールアドレス
            'password': 'SecurePassword123!',
            'name': 'New User',
            'age': 25,
            'gender': 'F',
            'phone_number': '0987654321',
            'joined': timezone.now().date(),
            'department_name': 'Test Department',
            'position': '社員'  # 有効な役職の選択肢
        }
        form = RegisterForm(data=form_data)
        if not form.is_valid():
            self.fail(f"RegisterFormのバリデーションに失敗しました: {form.errors}")
        self.assertTrue(form.is_valid())

    # ログインフォームが有効なユーザー資格情報で機能するか確認するテスト
    def test_login_form_valid(self):
        form_data = {
            'user_id': 'testuser',
            'password': 'SecurePassword123!'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    # シフトアップロードフォームが有効なCSVファイルを受け入れるか確認するテスト
    def test_shift_upload_form_valid(self):
        form_data = {}
        file_mock = SimpleUploadedFile('dummy.csv', b"dummy data for csv", content_type='text/csv')  # テスト用にSimpleUploadedFileを使用
        form = ShiftUploadForm(data=form_data, files={'csv_file': file_mock})
        if not form.is_valid():
            self.fail(f"ShiftUploadFormのバリデーションに失敗しました: {form.errors}")
        self.assertTrue(form.is_valid())

    # 休暇申請フォームが開始日が終了日より後の場合に失敗するか確認するテスト
    def test_leave_request_form_invalid_dates(self):
        form_data = {
            'leave_type': 1,  # `leave_type` が整数を期待するForeignKeyまたはChoiceFieldであると仮定
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() - timezone.timedelta(days=1),  # 終了日が開始日より前
            'applicant_comment': 'Need leave'
        }
        form = LeaveRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)  # 日付バリデーションのためのフィールド外エラーを期待

    # 自分自身の情報を編集する場合にフィールドが正しく無効化されているか確認するテスト
    def test_employee_edit_form_self_edit(self):
        form = EmployeeEditForm(instance=self.user, is_self=True)
        self.assertTrue(form.fields['account_id'].disabled)
        self.assertTrue(form.fields['joined'].disabled)
        self.assertTrue(form.fields['department_name'].disabled)
        self.assertTrue(form.fields['position'].disabled)

    # 上司が他の従業員の情報を編集する場合にフィールドが正しく無効化されているか確認するテスト
    def test_employee_edit_form_superior_edit(self):
        form = EmployeeEditForm(instance=self.user, is_superior=True)
        self.assertTrue(form.fields['account_id'].disabled)
        self.assertTrue(form.fields['joined'].disabled)
        self.assertTrue(form.fields['department_name'].disabled)
        self.assertTrue(form.fields['position'].disabled)

    # 従業員が自分自身のタイムスタンプ情報を編集できないことを確認するテスト
    def test_timestamp_edit_form_self_edit(self):
        timestamp = TimeStamp.objects.create(
            user=self.user,
            clock_in_time=timezone.now(),
            clock_out_time=timezone.now() + timezone.timedelta(hours=8)
        )
        form = TimeStampEditForm(instance=timestamp, is_self=True)
        self.assertTrue(form.fields['clock_in_time'].disabled)
        self.assertTrue(form.fields['clock_out_time'].disabled)

    # マネージャーが従業員のタイムスタンプ情報を編集できることを確認するテスト
    def test_timestamp_edit_form_manager_edit(self):
        timestamp = TimeStamp.objects.create(
            user=self.user,
            clock_in_time=timezone.now(),
            clock_out_time=timezone.now() + timezone.timedelta(hours=8)
        )
        form = TimeStampEditForm(instance=timestamp, is_manager=True)
        self.assertFalse(form.fields['clock_in_time'].disabled)
        self.assertFalse(form.fields['clock_out_time'].disabled)