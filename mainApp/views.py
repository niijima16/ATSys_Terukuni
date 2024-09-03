# views.py

import pandas as pd
import csv
from django.shortcuts import render, redirect
from django.utils.timezone import now, localtime
from .models import User_Master, Shift, TimeStamp
from .forms import LoginForm, ShiftUploadForm, RegisterForm
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
    today = now().date()
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
    month_shifts = Shift.objects.filter(user=user, date__gte=month_start, date__lte=today)
    month_timestamps = TimeStamp.objects.filter(user=user, clock_in_time__date__gte=month_start, clock_in_time__date__lte=today)

    total_worked_hours = 0
    total_overtime_hours = 0
    total_early_leave_hours = 0

    for shift, timestamp in zip(month_shifts, month_timestamps):
        worked, overtime, early_leave = calculate_hours(shift, timestamp)
        total_worked_hours += worked
        total_overtime_hours += overtime
        total_early_leave_hours += early_leave

    context = {
        'user_name': user.name,
        'today_worked_hours': today_worked_hours,
        'today_overtime_hours': today_overtime_hours,
        'today_early_leave_hours': today_early_leave_hours,
        'selected_date': selected_date,
        'selected_day_worked_hours': selected_worked_hours,
        'selected_day_overtime_hours': selected_overtime_hours,
        'selected_day_early_leave_hours': selected_early_leave_hours,
        'total_worked_hours': total_worked_hours,
        'total_overtime_hours': total_overtime_hours,
        'total_early_leave_hours': total_early_leave_hours,
        'today_date': today,
    }

    return render(request, 'topPage.html', context)

def calculate_hours(shift, timestamp):
    """
    Calculate worked hours, overtime, and early leave based on shift and timestamp.
    """
    if not shift or not timestamp:
        return 0, 0, 0

    # 今日の日付
    today = datetime.today().date()

    # シフトの開始・終了時刻を datetime オブジェクトとして設定（タイムゾーンなし）
    shift_start = datetime.combine(today, shift.start_time).replace(tzinfo=None)
    shift_end = datetime.combine(today, shift.end_time).replace(tzinfo=None)

    # 出勤・退勤時刻をタイムゾーンなしの datetime オブジェクトとして設定
    clock_in = timestamp.clock_in_time.replace(tzinfo=None)
    clock_out = timestamp.clock_out_time.replace(tzinfo=None)

    # 勤務時間の計算
    worked_hours = (clock_out - clock_in).total_seconds() / 3600.0

    # 残業と早退の計算
    overtime = max(0, (clock_out - shift_end).total_seconds() / 3600.0) if clock_out > shift_end else 0
    early_leave = max(0, (shift_end - clock_out).total_seconds() / 3600.0) if clock_out < shift_end else 0

    return worked_hours, overtime, early_leave

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