import pandas as pd
import csv
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import User_Master, Shift, TimeStamp
from .forms import LoginForm, ShiftUploadForm, RegisterForm
from django.contrib import messages
from datetime import datetime, timedelta

def homePage(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            try:
                user = User_Master.objects.get(account_id=account)
                if password == user.password:
                    request.session['user_name'] = user.name  # セッションにユーザー名を保存
                    return redirect('topPage')
                else:
                    error_message = 'パスワードが正しくありません。'
            except User_Master.DoesNotExist:
                error_message = 'アカウントが見つかりません。'
    else:
        form = LoginForm()

    return render(request, 'HomePage.html', {'form': form, 'error_message': error_message})

def topPage(request):
    user_name = request.session.get('user_name', 'ゲスト')
    try:
        user = User_Master.objects.get(name=user_name)
    except User_Master.DoesNotExist:
        user = None

    if request.method == 'POST':
        if 'clock_in' in request.POST:  # 出勤処理
            today = timezone.now().date()
            existing_clock_in = TimeStamp.objects.filter(user=user, clock_in_time__date=today).exists()
            if existing_clock_in:
                messages.error(request, '本日は既に出勤しております｡')
            else:
                TimeStamp.objects.create(
                    user=user,
                    clock_in_time=timezone.now()
                )
                messages.success(request, '出勤しました。')
        
        elif 'clock_out' in request.POST:  # 退勤処理
            try:
                time_stamp = TimeStamp.objects.filter(user=user, clock_in_time__date=timezone.now().date()).latest('clock_in_time')
                time_stamp.clock_out_time = timezone.now()
                time_stamp.save()
                messages.success(request, '退勤しました。')
            except TimeStamp.DoesNotExist:
                messages.error(request, '出勤記録が見つかりません。')

        return redirect('topPage')

    return render(request, 'topPage.html', {'user_name': user_name})

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
                    # ユーザーが存在しない場合のエラーハンドリング
                    continue

            # アップロード成功のメッセージを追加
            messages.success(request, f'{updated_shifts} 件のシフトが正常にアップロードされました。')

            return redirect('upload_shifts')  # アップロードページにリダイレクト

    else:
        form = ShiftUploadForm()
    return render(request, 'upload_shifts.html', {'form': form})