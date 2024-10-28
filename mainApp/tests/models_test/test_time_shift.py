from django.test import TestCase
from django.db import IntegrityError
from mainApp.models.time_shift import Shift
from mainApp.models.user_master import User_Master
from django.utils import timezone
from datetime import timedelta, time

class ShiftModelTest(TestCase):
    def setUp(self):
        # テスト用のユーザーを作成
        self.user = User_Master.objects.create(
            name="Test User",
            account_id="testuser@example.com",
            age=30,
            gender="M",
            phone_number="09012345678",
            joined=timezone.now().date(),
            department_name="Test Department",
            position="社員"
        )

    def test_shift_creation(self):
        # シフトインスタンスが正しく作成されることをテストします。
        shift = Shift.objects.create(
            user=self.user,
            date=timezone.now().date(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_time=timedelta(hours=1),
            shift_type='Regular'
        )

        # 各フィールドが正しく保存されているかをアサート
        self.assertEqual(shift.user, self.user)
        self.assertEqual(shift.start_time, time(9, 0))
        self.assertEqual(shift.end_time, time(17, 0))
        self.assertEqual(shift.break_time, timedelta(hours=1))
        self.assertEqual(shift.shift_type, 'Regular')
        self.assertFalse(shift.is_off_day)  # デフォルトで勤務日

    def test_shift_string_representation(self):
        # シフトインスタンスの文字列表現が正しいことをテストします。
        shift = Shift.objects.create(
            user=self.user,
            date=timezone.now().date(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            shift_type='Regular'
        )

        # 期待される文字列表現と一致するかをアサート
        expected_str = f"{self.user.employee_number} - {shift.date} ({shift.weekday}) - 09:00 to 17:00"
        self.assertEqual(str(shift), expected_str)

    def test_shift_with_no_times(self):
        # 開始時間と終了時間が設定されていない場合、休みの日としてマークされることをテストします。
        shift = Shift.objects.create(
            user=self.user,
            date=timezone.now().date()
        )

        # 休みの日として正しくマークされているかをアサート
        self.assertTrue(shift.is_off_day)
        self.assertEqual(shift.start_time, None)
        self.assertEqual(shift.end_time, None)

    def test_shift_weekday_and_is_weekend(self):
        # シフトの曜日と週末フラグが正しく設定されることをテストします。
        shift = Shift.objects.create(
            user=self.user,
            date=timezone.now().date(),
            start_time=time(9, 0),
            end_time=time(17, 0)
        )

        # 曜日と週末フラグが正しく設定されているかをアサート
        self.assertIn(shift.weekday, ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
        self.assertEqual(shift.is_weekend, shift.weekday in ['Saturday', 'Sunday'])

    def test_unique_constraint_on_user_and_date(self):
        # 同じユーザーと日付でシフトエントリが重複しないことを確認
        date = timezone.now().date()

        # 最初のシフトエントリを作成
        Shift.objects.create(user=self.user, date=date, start_time=time(9, 0), end_time=time(17, 0))
        
        # 同じユーザーと日付でシフトエントリを再度作成するとエラーが発生することを確認
        with self.assertRaises(IntegrityError):
            Shift.objects.create(user=self.user, date=date, start_time=time(10, 0), end_time=time(18, 0))

