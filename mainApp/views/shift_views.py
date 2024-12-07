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
            updated_shifts = 0  # 更新されたシフトの数をカウント
            failed_rows = []  # 失敗した行のリスト

            for row in reader:
                try:
                    user = User_Master.objects.get(employee_number=row['employee_number'])

                    # CSVの日付フォーマット 'YYYY/MM/DD' を 'YYYY-MM-DD' に変換
                    date = datetime.strptime(row['date'], '%Y/%m/%d').date()
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
                    updated_shifts += 1

                except User_Master.DoesNotExist:
                    failed_rows.append(f"社員番号 {row['employee_number']} のユーザーが見つかりません。")
                    continue
                except ValueError as e:
                    failed_rows.append(f"行エラー: {str(e)}（データ: {row}）")
                    continue

            # 成功メッセージを設定
            if updated_shifts > 0:
                messages.success(request, f'{updated_shifts} 件のシフトが正常にアップロードされました。')

            # 失敗メッセージを設定
            if failed_rows:
                messages.error(request, f"{len(failed_rows)} 件のシフトが失敗しました。詳細: " + " | ".join(failed_rows))

            return redirect('upload_shifts')  # アップロードページにリダイレクト

    else:
        form = ShiftUploadForm()
    return render(request, 'upload_shifts.html', {'form': form})
