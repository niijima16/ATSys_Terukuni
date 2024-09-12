# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import User_Master, Shift, TimeStamp, LeaveRequest, PaidLeave
from .forms import LoginForm, ShiftUploadForm, RegisterForm, LeaveRequestForm
from datetime import datetime, timedelta


# ホームページ用
def homePage(request):
    error_message = None
    form = LoginForm(request.POST or None)
    
    if request.method == 'POST':
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
    
    # セッションから employee_number を取得
    employee_number = request.session.get('employee_number')
    user_name = None

    if employee_number:
        try:
            user = User_Master.objects.get(employee_number=employee_number)
            user_name = user.name
        except User_Master.DoesNotExist:
            # ユーザーが存在しない場合の処理
            pass

    context = {
        'form': form,
        'error_message': error_message,
        'employee_number': employee_number,
        'user_name': user_name,
    }

    return render(request, 'HomePage.html', context)

# トップページ用
@login_required
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
    today_worked_hours, today_overtime_hours, today_early_leave_hours, today_late_arrival_hours = calculate_hours(today_shift, today_timestamp)

    # 選択された日付の勤務情報
    selected_worked_hours, selected_overtime_hours, selected_early_leave_hours, selected_late_arrival_hours = calculate_hours(selected_shift, selected_timestamp)

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

#残業早退用
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

                # 残り有給日数の更新
                try:
                    paid_leave.use_leave(requested_days)
                except ValueError as e:
                    messages.error(request, str(e))
                    return render(request, 'apply_leave.html', {'form': form})

            leave_request.approved = False  # 初期状態で申請は未承認
            leave_request.save()
            messages.success(request, '有給申請が正常に送信されました。')
            return redirect('topPage')
    else:
        form = LeaveRequestForm()

    return render(request, 'apply_leave.html', {'form': form})

# 有給承認用
@login_required
def approve_leave_request(request, leave_request_id):
    """
    有給申請の承認ビュー。上長がこのビューにアクセスして承認を行います。
    """
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)
    user = request.user  # 現在ログインしているユーザー

    # 上長でない場合、エラーメッセージを表示
    if user not in leave_request.get_superiors():
        messages.error(request, 'あなたにはこの申請を承認する権限がありません。')
        return redirect('leave_request_list')

    # すでに承認済みのユーザーでない場合、承認者リストに追加
    if user not in leave_request.approved_by.all():
        leave_request.approved_by.add(user)
        leave_request.save()
        messages.success(request, '有給申請を承認しました。')

    return redirect('leave_request_list')

@login_required
@login_required
def leave_request_list(request):
    # DjangoのUserモデルからユーザーを取得
    user = request.user
    try:
        # User_Masterをuser_idでフィルタリング
        user_master = User_Master.objects.get(user_id=user.id)
        leave_requests = LeaveRequest.objects.filter(user=user_master)
    except User_Master.DoesNotExist:
        # User_Masterが存在しない場合は空のクエリセットを設定
        leave_requests = LeaveRequest.objects.none()
        # 必要に応じてメッセージや通知を追加
        # messages.warning(request, 'User Master not found.')

    return render(request, 'leave_requests.html', {'leave_requests': leave_requests})

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

