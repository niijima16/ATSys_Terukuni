# mainApp/views/auth_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from mainApp.models import User_Master, PaidLeave, Shift, TimeStamp
from mainApp.forms import LoginForm
from mainApp.decorators import custom_login_required
from mainApp.utils import calculate_hours
from datetime import datetime

# カスタムログイン機能を作成
def homePage(request):
    error_message = None
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST':
        if form.is_valid():
            account = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            try:
                # ユーザーが存在するか確認
                user = User_Master.objects.get(account_id=account)
                
                # パスワード認証（ハッシュ化なし、プレーンテキストでチェック）
                if password == user.password:
                    request.session['employee_number'] = user.employee_number  # セッションにemployee_numberを保存
                    return redirect('topPage')
                else:
                    error_message = 'パスワードが正しくありません。'
            except User_Master.DoesNotExist:
                error_message = 'アカウントが見つかりません。'
    
    # セッションから employee_number を取得
    employee_number = request.session.get('employee_number')
    user_name = None

    if employee_number:
        try:
            user = User_Master.objects.get(employee_number=employee_number)
            user_name = user.name
        except User_Master.DoesNotExist:
            pass

    context = {
        'form': form,
        'error_message': error_message,
        'employee_number': employee_number,
        'user_name': user_name,
    }

    return render(request, 'HomePage.html', context)

# トップページ用
@custom_login_required
def topPage(request):
    employee_number = request.session.get('employee_number')  # セッションからemployee_numberを取得
    user = User_Master.objects.get(employee_number=employee_number)

    # 今日の日付
    today = datetime.today().date()
    selected_date = request.GET.get('date', today)
    selected_date = today if selected_date == "" else selected_date

    # 勤務情報の取得
    today_shift = Shift.objects.filter(user=user, date=today).first()
    today_timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=today).first()
    selected_shift = Shift.objects.filter(user=user, date=selected_date).first()
    selected_timestamp = TimeStamp.objects.filter(user=user, clock_in_time__date=selected_date).first()

    # 勤務情報の計算
    today_worked_hours, today_overtime_hours, today_early_leave_hours, today_late_arrival_hours = calculate_hours(today_shift, today_timestamp)
    selected_worked_hours, selected_overtime_hours, selected_early_leave_hours, selected_late_arrival_hours = calculate_hours(selected_shift, selected_timestamp)

    # 今月の勤務情報
    month_start = today.replace(day=1)
    monthly_summary = TimeStamp.get_monthly_summary(user, month_start, today)

    # 有給の取得
    try:
        paid_leave = PaidLeave.objects.get(user=user)
    except PaidLeave.DoesNotExist:
        paid_leave = PaidLeave.objects.create(user=user)

    context = {
        'user_name': user.name,
        'today_worked_hours': today_worked_hours,
        'today_overtime_hours': today_overtime_hours,
        'today_early_leave_hours': today_early_leave_hours,
        'today_late_arrival_hours': today_late_arrival_hours,
        'selected_date': selected_date,
        'selected_day_worked_hours': selected_worked_hours,
        'selected_day_overtime_hours': selected_overtime_hours,
        'selected_day_early_leave_hours': selected_early_leave_hours,
        'selected_day_late_arrival_hours': selected_late_arrival_hours,
        'total_worked_hours': monthly_summary['total_worked_hours'],
        'total_overtime_hours': monthly_summary['total_overtime_hours'],
        'total_early_leave_hours': monthly_summary['total_early_leave_hours'],
        'total_late_arrival_hours': monthly_summary['total_late_arrival_hours'],
        'today_date': today,
        'paid_leave': paid_leave,
        'employee_number': employee_number,
    }

    if request.method == 'POST':
        if 'clock_in' in request.POST:
            # 出勤処理
            today = datetime.today().date()
            existing_entry = TimeStamp.objects.filter(user=user, clock_in_time__date=today, clock_out_time__isnull=True).exists()
            if existing_entry:
                messages.warning(request, '既に出勤記録があります。')
            else:
                clock_in_time = timezone.now()
                TimeStamp.objects.create(user=user, clock_in_time=clock_in_time)
                messages.success(request, '出勤が記録されました。')
        elif 'clock_out' in request.POST:
            # 退勤処理
            today = datetime.today().date()
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
