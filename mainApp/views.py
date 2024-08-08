import pandas as pd
import csv
from django.shortcuts import render, redirect
from django.utils import timezone
from .models import User_Master, Shift, TimeSheet
from .forms import ShiftUploadForm, LoginForm, CSVUploadForm, RegisterForm
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

def parse_duration(duration_str):
    try:
        # Try splitting the time string into hours, minutes, and seconds
        time_parts = duration_str.split(':')
        if len(time_parts) != 3:
            raise ValueError(f"Incorrect format for break_time: {duration_str}")
        hours, minutes, seconds = map(int, time_parts)
        return timedelta(hours=hours, minutes=minutes, seconds=seconds)
    except ValueError as e:
        raise ValueError(f"Error parsing duration '{duration_str}': {e}")

def upload_shifts(request):
    if request.method == "POST":
        form = ShiftUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            try:
                for row in reader:
                    try:
                        # ユーザー名からUser_Masterを取得
                        user = User_Master.objects.get(name=row['name'])

                        # 日付を文字列からdatetime.dateオブジェクトに変換
                        date_obj = datetime.strptime(row['date'], '%Y-%m-%d').date()

                        # 空欄の場合は「休み」として処理
                        start_time = datetime.strptime(row['start_time'], '%H:%M:%S').time() if row['start_time'] else None
                        end_time = datetime.strptime(row['end_time'], '%H:%M:%S').time() if row['end_time'] else None
                        break_time = parse_duration(row['break_time']) if row['break_time'] else timedelta(hours=0)  # デフォルトを0時間に設定

                        # Shiftオブジェクトを作成し保存
                        shift = Shift(
                            user=user,
                            date=date_obj,
                            start_time=start_time,
                            end_time=end_time,
                            break_time=break_time,
                            shift_type=row.get('shift_type', ''),
                            # 「休み」を示すフィールドを設定する場合
                            is_weekend=True if not start_time and not end_time else False
                        )
                        shift.save()
                    except Exception as e:
                        print(f"Error processing row {row}: {e}")
                messages.success(request, "Shifts uploaded successfully!")
            except Exception as e:
                messages.error(request, f"Error uploading shifts: {e}")
    else:
        form = ShiftUploadForm()
    return render(request, 'upload_shifts.html', {'form': form})