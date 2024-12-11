# mainApp/views/shift_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from mainApp.models import User_Master, Shift
from mainApp.forms import ShiftUploadForm
from datetime import datetime, timedelta
import csv

# シフトをアップロード用
def upload_shifts(request):
    if request.method == 'POST':
        form = ShiftUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = form.cleaned_data['csv_file']
            decoded_file = csv_file.read().decode('utf-8').splitlines()
            reader = csv.DictReader(decoded_file)
            updated_shifts = 0
            failed_rows = []  # エラー行を記録

            for row in reader:
                try:
                    user = User_Master.objects.get(employee_number=row['employee_number'])

                    # 日付と時間の処理
                    date = datetime.strptime(row['date'], '%Y/%m/%d').date()
                    start_time = datetime.strptime(row['start_time'], '%H:%M:%S').time() if row['start_time'] else None
                    end_time = datetime.strptime(row['end_time'], '%H:%M:%S').time() if row['end_time'] else None

                    # 休憩時間の処理（未設定の場合はNoneに設定）
                    break_time = None
                    if row['break_time']:
                        (hours, minutes, seconds) = map(int, row['break_time'].split(':'))
                        break_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)

                    # シフトの保存
                    Shift.objects.update_or_create(
                        user=user,
                        date=date,
                        defaults={
                            'start_time': start_time,
                            'end_time': end_time,
                            'break_time': break_time,
                        }
                    )
                    updated_shifts += 1

                except Exception as e:
                    failed_rows.append(f"行エラー: {row} - {str(e)}")
                    continue

            # 成功と失敗メッセージ
            if updated_shifts > 0:
                messages.success(request, f'{updated_shifts} 件のシフトが正常にアップロードされました。')
            if failed_rows:
                messages.error(request, f'{len(failed_rows)} 件のシフトが失敗しました。詳細: ' + ', '.join(failed_rows))

            return redirect('upload_shifts')

    else:
        form = ShiftUploadForm()
    return render(request, 'upload_shifts.html', {'form': form})
