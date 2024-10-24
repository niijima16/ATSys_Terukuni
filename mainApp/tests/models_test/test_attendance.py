# tests/test_attendance_model.py
from django.test import TestCase
from django.db import IntegrityError
from mainApp.models.attendance import Attendance
from mainApp.models.user_master import User_Master
from mainApp.models.leave_type import LeaveType
from django.utils import timezone

class AttendanceModelTest(TestCase):
    def setUp(self):
        # テスト用のユーザーと休暇タイプを作成
        self.user = User_Master.objects.create(
            name='Test User',
            account_id='12345',
            age=30,  # age フィールドを追加
            gender='M',  # gender フィールドを追加
            phone_number='09012345678',
            joined=timezone.now().date(),
            department_name='Test Department',
            position='社員'
        )
        self.leave_type = LeaveType.objects.create(name='Annual Leave')

    def test_create_attendance_entry(self):
        # 勤怠エントリを作成し、適切に保存されているかを確認
        attendance = Attendance.objects.create(
            user=self.user,
            date=timezone.now().date(),
            status='vacation',
            leave_type=self.leave_type,
            notes='Annual vacation'
        )

        # 各フィールドが正しく保存されているかをアサート
        self.assertEqual(attendance.user, self.user)
        self.assertEqual(attendance.status, 'vacation')
        self.assertEqual(attendance.leave_type, self.leave_type)
        self.assertEqual(attendance.notes, 'Annual vacation')

    def test_attendance_unique_constraint(self):
        # 同じユーザーと日付で勤怠エントリが重複しないことを確認
        date = timezone.now().date()

        # 最初の勤怠エントリを作成
        Attendance.objects.create(user=self.user, date=date, status='present')
        
        # 同じユーザーと日付で勤怠エントリを再度作成するとエラーが発生することを確認
        with self.assertRaises(IntegrityError):
            Attendance.objects.create(user=self.user, date=date, status='vacation')

    def test_attendance_with_null_leave_type(self):
        # 休暇タイプが指定されていない場合でも勤怠エントリが作成できることを確認
        attendance = Attendance.objects.create(user=self.user, date=timezone.now().date(), status='sick')

        # leave_type が None であることをアサート
        self.assertIsNone(attendance.leave_type)
        self.assertEqual(attendance.status, 'sick')

    def test_attendance_str_representation(self):
        # 勤怠エントリの文字列表現が正しいことを確認
        attendance = Attendance.objects.create(user=self.user, date=timezone.now().date(), status='present')

        # 期待される文字列表現と一致するかをアサート
        expected_str = f"{self.user.name} - {attendance.date} - {attendance.get_status_display()}"
        self.assertEqual(str(attendance), expected_str)
