# tests/test_time_stamp_model.py
from django.test import TestCase
from mainApp.models.user_master import User_Master
from mainApp.models.time_stamp import TimeStamp
from mainApp.models.time_shift import Shift
from django.utils import timezone
from datetime import datetime, timedelta, time

class TimeStampModelUnitTest(TestCase):
    def setUp(self):
        # テスト用のユーザーとタイムスタンプを作成
        self.user = User_Master.objects.create(
            name='Test User',
            account_id='12345',
            age=30,
            gender='M',
            phone_number='09012345678',
            joined=timezone.now().date(),
            department_name='Test Department',
            position='社員'
        )
        self.shift = Shift.objects.create(
            user=self.user,
            date=timezone.now().date(),
            start_time=time(9, 0),
            end_time=time(17, 0),
            break_time=timedelta(minutes=60)
        )
        self.clock_in_time = timezone.make_aware(datetime.combine(self.shift.date, self.shift.start_time))
        self.clock_out_time = timezone.make_aware(datetime.combine(self.shift.date, self.shift.end_time))
        self.timestamp = TimeStamp.objects.create(user=self.user, shift=self.shift, clock_in_time=self.clock_in_time, clock_out_time=self.clock_out_time)

    def test_worked_hours_without_overtime_or_early_leave(self):
        # 勤務時間を計算し、期待される勤務時間と一致するかを確認
        worked_hours = self.timestamp.calculate_worked_hours()
        shift_start_datetime = datetime.combine(self.shift.date, self.shift.start_time)
        shift_end_datetime = datetime.combine(self.shift.date, self.shift.end_time)
        expected_hours = (shift_end_datetime - shift_start_datetime).seconds / 3600 - self.shift.break_time.seconds / 3600
        self.assertEqual(worked_hours, expected_hours)

    def test_overtime_when_clock_out_after_shift_end(self):
        # 退勤時間をシフト終了時間より後に設定（残業あり）
        self.timestamp.clock_out_time = self.clock_out_time + timedelta(hours=2)
        self.timestamp.save()

        # 残業時間を計算し、期待される残業時間と一致するかを確認
        overtime_hours = self.timestamp.calculate_overtime()
        expected_overtime = 2.0  # 2時間の残業
        self.assertEqual(overtime_hours, expected_overtime)

    def test_early_leave_when_clock_out_before_shift_end(self):
        # 退勤時間をシフト終了時間より前に設定（早退あり）
        self.timestamp.clock_out_time = self.clock_out_time - timedelta(hours=1)
        self.timestamp.save()

        # 早退時間を計算し、期待される早退時間と一致するかを確認
        early_leave_hours = self.timestamp.calculate_early_leave()
        expected_early_leave = 1.0  # 1時間の早退
        self.assertEqual(early_leave_hours, expected_early_leave)

    def test_late_arrival_when_clock_in_after_shift_start(self):
        # 出勤時間をシフト開始時間より後に設定（遅刻あり）
        self.timestamp.clock_in_time = self.clock_in_time + timedelta(hours=1)
        self.timestamp.save()

        # 遅刻時間を計算し、期待される遅刻時間と一致するかを確認
        late_arrival_hours = self.timestamp.calculate_late_arrival()
        expected_late_arrival = 1.0  # 1時間の遅刻
        self.assertEqual(late_arrival_hours, expected_late_arrival)
