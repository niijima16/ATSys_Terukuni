from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta, time
from mainApp.models.time_stamp import TimeStamp
from mainApp.models.time_shift import Shift
from mainApp.models.user_master import User_Master

class TimeStampModelTest(TestCase):
    def setUp(self):
        # テスト用のユーザーとシフトを作成
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
        self.shift = Shift.objects.create(
            user=self.user,
            date=timezone.now().date(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_time=timedelta(hours=1),
            shift_type='Regular'
        )

    def test_calculate_worked_hours(self):
        # 勤務時間の計算が正しいことをテスト
        timestamp = TimeStamp.objects.create(
            user=self.user,
            shift=self.shift,
            clock_in_time=timezone.make_aware(datetime.combine(self.shift.date, time(9, 0))),
            clock_out_time=timezone.make_aware(datetime.combine(self.shift.date, time(17, 0)))
        )

        expected_hours = 7  # 9:00-17:00 の8時間から1時間の休憩を引く
        self.assertEqual(timestamp.calculate_worked_hours(), expected_hours)

    def test_calculate_overtime(self):
        # 残業時間の計算が正しいことをテスト
        timestamp = TimeStamp.objects.create(
            user=self.user,
            shift=self.shift,
            clock_in_time=timezone.make_aware(datetime.combine(self.shift.date, time(9, 0))),
            clock_out_time=timezone.make_aware(datetime.combine(self.shift.date, time(19, 0)))
        )

        expected_overtime = 2  # 17:00以降に2時間の残業
        self.assertEqual(timestamp.calculate_overtime(), expected_overtime)

    def test_calculate_early_leave(self):
        # 早退時間の計算が正しいことをテスト
        timestamp = TimeStamp.objects.create(
            user=self.user,
            shift=self.shift,
            clock_in_time=timezone.make_aware(datetime.combine(self.shift.date, time(9, 0))),
            clock_out_time=timezone.make_aware(datetime.combine(self.shift.date, time(15, 0)))
        )

        expected_early_leave = 2  # 17:00前に2時間早退
        self.assertEqual(timestamp.calculate_early_leave(), expected_early_leave)

    def test_calculate_late_arrival(self):
        # 遅刻時間の計算が正しいことをテスト
        timestamp = TimeStamp.objects.create(
            user=self.user,
            shift=self.shift,
            clock_in_time=timezone.make_aware(datetime.combine(self.shift.date, time(10, 0))),  # 1時間遅刻
            clock_out_time=timezone.make_aware(datetime.combine(self.shift.date, time(17, 0)))
        )

        expected_late_arrival = 1  # 9:00の開始時間から1時間遅刻
        self.assertEqual(timestamp.calculate_late_arrival(), expected_late_arrival)

    def test_string_representation(self):
        # タイムスタンプの文字列表現が正しいことをテスト
        timestamp = TimeStamp.objects.create(
            user=self.user,
            shift=self.shift,
            clock_in_time=timezone.make_aware(datetime.combine(self.shift.date, time(9, 0))),
            clock_out_time=timezone.make_aware(datetime.combine(self.shift.date, time(17, 0)))
        )

        expected_str = f"{self.user.name} - {timestamp.clock_in_time} to {timestamp.clock_out_time}"
        self.assertEqual(str(timestamp), expected_str)
