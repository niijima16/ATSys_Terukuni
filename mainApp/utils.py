# mainApp/utils.py

from datetime import datetime
from django.utils import timezone

def calculate_hours(shift, timestamp):
    """
    勤務時間、残業時間、早退時間、遅刻時間をシフトとタイムスタンプに基づいて計算する。
    """
    if not shift or not timestamp:
        return 0, 0, 0, 0  # 遅刻時間も追加

    # シフトとタイムスタンプの日時をタイムゾーン対応に変換
    shift_date = shift.date
    shift_start = datetime.combine(shift_date, shift.start_time)
    shift_end = datetime.combine(shift_date, shift.end_time)

    # shift_startとshift_endがnaive（タイムゾーンなし）の場合、timezoneを付与
    if timezone.is_naive(shift_start):
        shift_start = timezone.make_aware(shift_start, timezone.get_current_timezone())
    if timezone.is_naive(shift_end):
        shift_end = timezone.make_aware(shift_end, timezone.get_current_timezone())

    clock_in = timestamp.clock_in_time
    clock_out = timestamp.clock_out_time

    # clock_inとclock_outがnaive（タイムゾーンなし）の場合、timezoneを付与
    if clock_in and timezone.is_naive(clock_in):
        clock_in = timezone.make_aware(clock_in, timezone.get_current_timezone())
    if clock_out and timezone.is_naive(clock_out):
        clock_out = timezone.make_aware(clock_out, timezone.get_current_timezone())

    # 勤務時間の計算
    if clock_in and clock_out:
        # 出勤から退勤までの総時間を計算
        worked_time = (clock_out - clock_in)

        # 休憩時間を差し引く
        worked_time -= shift.break_time
        worked_hours = max(worked_time.total_seconds() / 3600.0, 0)  # 勤務時間は負の値にならないようにする

        # 早出の時間（シフト開始時間より前に出勤した場合）
        early_overtime = max(0, (shift_start - clock_in).total_seconds() / 3600.0) if clock_in < shift_start else 0

        # 通常の残業時間（シフト終了時間を超えた場合）
        late_overtime = max(0, (clock_out - shift_end).total_seconds() / 3600.0) if clock_out > shift_end else 0

        # 早退の計算（シフト終了時間前に退勤した場合）
        early_leave = max(0, (shift_end - clock_out).total_seconds() / 3600.0) if clock_out < shift_end else 0

        # 遅刻の計算（シフト開始時間より後に出勤した場合）
        late_arrival = max(0, (clock_in - shift_start).total_seconds() / 3600.0) if clock_in > shift_start else 0

        # 小数点以下2桁に丸める
        return round(worked_hours, 2), round(early_overtime + late_overtime, 2), round(early_leave, 2), round(late_arrival, 2)
    else:
        return 0, 0, 0, 0
