# views.py

import pandas as pd
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import User_Master, Shift, TimeStamp, LeaveRequest, PaidLeave
from .forms import LoginForm, ShiftUploadForm, RegisterForm, LeaveRequestForm
from django.contrib import messages
from datetime import datetime, timedelta

# ホームページ用
def homePage(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            try:
                user = User_Master.objects.get(account_id=account)
                if password == user.password:  # パスワード認証の改善を推奨
                    request.session['employee_number'] = user.employee_number  # セッションにemployee_numberを保存
                    return redirect('topPage')
                else:
                    error_message = 'パスワードが正しくありません。'
            except User_Master.DoesNotExist:
                error_message = 'アカウントが見つかりません。'
    else:
        form = LoginForm()

    return render(request, 'HomePage.html', {'form': form, 'error_message': error_message})

# トップページ用
def topPage(request):
    employee_number = request.session.get('employee_number')  # セッションからemployee_numberを取得
    if not employee_number:
        return redirect('homePage')  # セッションが無効な場合はログインページにリダイレクト

    user = User_Master.objects.get(employee_number=employee_number)

    # 今日の日付
    today = datetime.today().date()
    selected_date = request.GET.get('date', today)
    selected_date = today if selected_date == "" else selected_date

    # 当日と選択した日の勤務情報取得
    today_shift = Shift.objects.filter(user=user, date=today).first()
    today_timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=today).first()
    selected_shift = Shift.objects.filter(user=user, date=selected_date).first()
    selected_timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=selected_date).first()

    # 今日の勤務情報
    today_worked_hours, today_overtime_hours, today_early_leave_hours = calculate_hours(today_shift, today_timestamp)

    # 選択された日付の勤務情報
    selected_worked_hours, selected_overtime_hours, selected_early_leave_hours = calculate_hours(selected_shift, selected_timestamp)

    # 今月の勤務情報
    month_start = today.replace(day=1)
    month_timestamps = TimeStamp.objects.filter(user=user, clock_in_time__date__gte=month_start, clock_in_time__date__lte=today)

    monthly_summary = TimeStamp.get_monthly_summary(user, month_start, today)

    # 有給の取得
    try:
        paid_leave = PaidLeave.objects.get(user=user)
    except PaidLeave.DoesNotExist:
        paid_leave = PaidLeave.objects.create(user=user)  # 新しく作成する場合もあります

    context = {
        'user_name': user.name,
        'today_worked_hours': today_worked_hours,
        'today_overtime_hours': today_overtime_hours,
        'today_early_leave_hours': today_early_leave_hours,
        'selected_date': selected_date,
        'selected_day_worked_hours': selected_worked_hours,
        'selected_day_overtime_hours': selected_overtime_hours,
        'selected_day_early_leave_hours': selected_early_leave_hours,
        'total_worked_hours': monthly_summary['total_worked_hours'],
        'total_overtime_hours': monthly_summary['total_overtime_hours'],
        'total_early_leave_hours': monthly_summary['total_early_leave_hours'],
        'today_date': today,
        'paid_leave': paid_leave,
        'employee_number': employee_number,
    }

    return render(request, 'topPage.html', context)

#残業早退用
def calculate_hours(shift, timestamp):
    """
    勤務時間、残業時間、早退時間をシフトとタイムスタンプに基づいて計算する。
    """
    if not shift or not timestamp:
        return 0, 0, 0

    # シフトとタイムスタンプの日時をタイムゾーン対応に変換
    shift_date = shift.date  # シフトの日付を使用
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

        # 総残業時間は早出残業と通常の残業の合計
        overtime = early_overtime + late_overtime

        # 早退の計算（シフト終了時間前に退勤した場合）
        early_leave = max(0, (shift_end - clock_out).total_seconds() / 3600.0) if clock_out < shift_end and clock_out > shift_start else 0

        return worked_hours, overtime, early_leave
    else:
        return 0, 0, 0

# 有給申請用
def apply_leave(request):
    employee_number = request.session.get('employee_number')  # セッションからemployee_numberを取得
    if not employee_number:
        return redirect('homePage')  # セッションが無効な場合はログインページにリダイレクト

    user = get_object_or_404(User_Master, employee_number=employee_number)

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = user

            # 有給残日数のチェック
            if leave_request.leave_type == 'Paid':
                paid_leave = PaidLeave.objects.get(user=user)
                requested_days = (leave_request.end_date - leave_request.start_date).days + 1

                if requested_days > paid_leave.remaining_days:
                    messages.error(request, '申請日数が残り有給日数を超えています。')
                    return render(request, 'apply_leave.html', {'form': form})

            leave_request.save()
            messages.success(request, '有給申請が正常に送信されました。')
            return redirect('topPage')
    else:
        form = LeaveRequestForm()

    return render(request, 'apply_leave.html', {'form': form})

# 社員情報登録用
def registerPage(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homePage')
    else:
        form = RegisterForm()
    return render(request, 'Registration.html', {'form': form})

# シフトをアップロード用
def upload_shifts(request):
    if request.method == 'POST':
        form = ShiftUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            updated_shifts = 0  # 更新されたシフトの数をカウント

            for row in reader:
                try:
                    user = User_Master.objects.get(employee_number=row['employee_number'])
                    
                    date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    start_time = row['start_time'] if row['start_time'] else None
                    end_time = row['end_time'] if row['end_time'] else None
                    
                    break_time_str = row['break_time'] if row['break_time'] else '0:00:00'
                    (hours, minutes, seconds) = map(int, break_time_str.split(':'))
                    break_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)
                    
                    # 既存のシフトを確認し、更新または作成
                    shift, created = Shift.objects.update_or_create(
                        user=user,
                        date=date,
                        defaults={
                            'start_time': start_time,
                            'end_time': end_time,
                            'break_time': break_time,
                        }
                    )
                    if created:
                        updated_shifts += 1

                except User_Master.DoesNotExist:
                    messages.error(request, f"ユーザー {row['employee_number']} が見つかりません。")
                    continue
                except Exception as e:
                    messages.error(request, f"エラーが発生しました: {str(e)}")
                    continue

            # アップロード成功のメッセージを追加
            messages.success(request, f'{updated_shifts} 件のシフトが正常にアップロードされました。')

            return redirect('upload_shifts')  # アップロードページにリダイレクト

    else:
        form = ShiftUploadForm()
    return render(request, 'upload_shifts.html', {'form': form})

# ログアウト
def logout(request):
    request.session.flush()  # セッションをクリア
    return redirect('homePage')  # ログインページにリダイレクト