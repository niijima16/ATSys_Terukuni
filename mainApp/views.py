import pandas as pd
import csv
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import User_Master, Shift, TimeSheet
from .forms import ShiftUploadForm, LoginForm, CSVUploadForm, RegisterForm
from django.contrib import messages
from datetime import datetime

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
    user_name = request.session.get('user_name', 'ゲスト')  # セッションからユーザー名を取得
    user = User_Master.objects.get(name=user_name)
    if request.method == 'POST' :
        if 'clock_in' in request.POST: # 出勤処理
            TimeSheet.objects.create(
                user = user,
                date = timezone.now().date(),
                start_time = timezone.now().time()
            )
        elif 'clock_out' in request.POST: # 退勤処理
            try:
                timesheet = TimeSheet.objects.filter(user=user, date=timezone.now().date()).latest('start_time')
                timesheet.end_time = timezone.now().time()
                timesheet.save()
            except TimeSheet.DoesNotExist:
                pass
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

# シフトアップロード用
# def upload_shifts(request):
#     if request.method == 'POST':
#         form = ShiftUploadForm(request.POST, request.FILES)
#         if form.is_valid():
#             excel_file = request.FILES['file']
#             df = pd.read_excel(excel_file, engine='openpyxl')

#             shift_objects = []
#             errors = []

#             for index, row in df.iterrows():
#                 try:
#                     user = User_Master.objects.get(name=row['name'])

#                     # 日付のバリデーション
#                     try:
#                         date = pd.to_datetime(row['date']).date()
#                     except ValueError:
#                         errors.append(f"行 {index + 1}: 無効な日付形式 - {row['date']}")
#                         continue

#                     # 時間のバリデーション
#                     try:
#                         start_time = datetime.strptime(str(row['start_time']), '%H:%M:%S').time()
#                         end_time = datetime.strptime(str(row['end_time']), '%H:%M:%S').time()
#                     except ValueError:
#                         errors.append(f"行 {index + 1}: 無効な時間形式 - 開始: {row['start_time']}, 終了: {row['end_time']}")
#                         continue

#                     # 休憩時間のバリデーション
#                     try:
#                         break_time = pd.to_timedelta(row['break_time'])
#                     except ValueError:
#                         errors.append(f"行 {index + 1}: 無効な休憩時間形式 - {row['break_time']}")
#                         continue

#                     # シフトオブジェクトの作成
#                     shift_objects.append(Shift(
#                         user=user,
#                         date=date,
#                         start_time=start_time,
#                         end_time=end_time,
#                         break_time=break_time,
#                         shift_type=row['shift_type']
#                     ))
#                 except User_Master.DoesNotExist:
#                     errors.append(f"行 {index + 1}: ユーザー '{row['name']}' が存在しません")
#                 except Exception as e:
#                     errors.append(f"行 {index + 1}: データの保存中にエラーが発生しました - {str(e)}")

#             if shift_objects:
#                 Shift.objects.bulk_create(shift_objects)
#                 messages.success(request, f"{len(shift_objects)}件のシフトが正常にアップロードされました")

#             for error in errors:
#                 messages.error(request, error)

#             return redirect('shift_success')

#     else:
#         form = ShiftUploadForm()
#     return render(request, 'upload_shifts.html', {'form': form})

# アップロード判断：成功
def shift_success(request):
    return render(request, 'shift_success.html') 

def upload_shifts(request):
    if request.method == 'POST':
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['csv_file']
            if not csv_file.name.endswith('.csv'):
                messages.error(request, 'CSVファイルをアップロードしてください。')
                return redirect('upload_shifts')
            try:
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.reader(decoded_file)
                for row in reader:
                    if len(row) != 5:  # 必要なカラム数
                        continue
                    user_id, date, start_time, end_time, break_time = row
                    # ユーザーIDでユーザーを取得
                    user = User_Master.objects.get(pk=user_id)
                    Shift.objects.create(
                        user=user,
                        date=date,
                        start_time=start_time,
                        end_time=end_time,
                        break_time=break_time
                    )
                messages.success(request, 'シフトが正常にアップロードされました。')
            except Exception as e:
                messages.error(request, f'エラーが発生しました: {e}')
            return redirect('upload_shifts')
    else:
        form = CSVUploadForm()
    return render(request, 'upload_shifts.html', {'form': form})