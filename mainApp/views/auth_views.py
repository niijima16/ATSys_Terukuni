# mainApp/views/auth_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.timezone import now
from mainApp.models import User_Master, PaidLeave, Shift, TimeStamp
from mainApp.forms import LoginForm
from mainApp.decorators import custom_login_required
from mainApp.utils import calculate_hours
from datetime import datetime
from django.utils import timezone
from django.utils.timezone import make_aware, is_aware
import hashlib

# カスタムログイン機能を作成
def homePage(request):
    error_message = None
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            account = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            encrypted_password = hashlib.sha256(password.encode()).hexdigest()  # 入力されたパスワードを暗号化

            try:
                # ユーザーが存在するか確認
                user = User_Master.objects.get(account_id=account)

                # データベース内の暗号化済みパスワードと比較
                if encrypted_password == user.password:
                    request.session['employee_number'] = user.employee_number  # セッションに employee_number を保存
                    return redirect('topPage')
                else:
                    error_message = 'パスワードが正しくありません。'
            except User_Master.DoesNotExist:
                error_message = 'アカウントが見つかりません。'

    context = {
        'form': form,
        'error_message': error_message,
    }
    return render(request, 'HomePage.html', context)

# トップページ用
@custom_login_required
def topPage(request):
    employee_number = request.session.get('employee_number')  # セッションからemployee_numberを取得
    user = User_Master.objects.get(employee_number=employee_number)

    # 今日の日付
    today = datetime.today().date()

    # 選択した日付を取得（無効な値の場合は今日の日付を使用）
    selected_date = request.GET.get('date')
    if selected_date:
        try:
            selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today
    else:
        selected_date = today

    # 今日の勤務情報
    today_shift = Shift.objects.filter(user=user, date=today).first()
    today_timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=today).first()

    today_worked_hours, today_overtime_hours, today_early_leave_hours, today_late_arrival_hours = calculate_hours(today_shift, today_timestamp)

    # 選択した日付の勤務情報
    selected_shift = Shift.objects.filter(user=user, date=selected_date).first()
    selected_timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=selected_date).first()

    selected_worked_hours, selected_overtime_hours, selected_early_leave_hours, selected_late_arrival_hours = calculate_hours(selected_shift, selected_timestamp)

    selected_day_summary = {
        'worked_hours': selected_worked_hours,
        'overtime_hours': selected_overtime_hours,
        'early_leave_hours': selected_early_leave_hours,
        'late_arrival_hours': selected_late_arrival_hours,
    }

    # 今月の勤務情報
    month_start = today.replace(day=1)
    monthly_summary = TimeStamp.get_monthly_summary(user=user, month_start=month_start, today=today)

    # 勤務時間に残業時間を加えた出力
    total_worked_hours_with_overtime = monthly_summary['total_worked_hours'] + monthly_summary['total_overtime_hours']

    # 有給の取得
    try:
        paid_leave = PaidLeave.objects.get(user=user)
    except PaidLeave.DoesNotExist:
        paid_leave = PaidLeave.objects.create(user=user)

    context = {
        'user_name': user.name,
        'today_worked_hours': round(today_worked_hours, 2),
        'today_overtime_hours': round(today_overtime_hours, 2),
        'today_early_leave_hours': round(today_early_leave_hours, 2),
        'today_late_arrival_hours': round(today_late_arrival_hours, 2),
        'selected_date': selected_date,
        'selected_day_summary': selected_day_summary,
        'month_summary': {
            'total_worked_hours': round(total_worked_hours_with_overtime, 2),
            'total_overtime_hours': round(monthly_summary['total_overtime_hours'], 2),
            'total_early_leave_hours': round(monthly_summary['total_early_leave_hours'], 2),
            'total_late_arrival_hours': round(monthly_summary['total_late_arrival_hours'], 2),
        },
        'today_date': today,
        'paid_leave': paid_leave,
        'employee_number': employee_number,
    }

    if request.method == 'POST':
        if 'clock_in' in request.POST:
            # 出勤処理
            existing_entry = TimeStamp.objects.filter(user=user, clock_in_time__date=today, clock_out_time__isnull=True).exists()
            if existing_entry:
                messages.warning(request, '既に出勤記録があります。')
            else:
                clock_in_time = timezone.now()
                TimeStamp.objects.create(user=user, clock_in_time=clock_in_time)
                messages.success(request, '出勤が記録されました。')
        elif 'clock_out' in request.POST:
            # 退勤処理
            timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=today, clock_out_time__isnull=True).last()
            if timestamp:
                clock_out_time = timezone.now()
                timestamp.clock_out_time = clock_out_time
                timestamp.save()
                messages.success(request, '退勤が記録されました。')
            else:
                messages.error(request, '出勤記録が見つかりません。')
        return redirect('topPage')

    return render(request, 'topPage.html', context)



# ログアウト
def logout(request):
    # セッションから特定のキーのみ削除
    if 'employee_number' in request.session:
        del request.session['employee_number']
    # メッセージを表示してログインページにリダイレクト
    messages.success(request, 'ログアウトしました。')
    return redirect('homePage')
