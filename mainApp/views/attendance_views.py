# mainApp/views/attendance_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from mainApp.models import User_Master, TimeStamp
from mainApp.forms import TimeStampEditForm
from mainApp.decorators import custom_login_required, manager_required

# 勤怠情報編集用
@custom_login_required
@manager_required
def edit_timestamp(request):
    manager = User_Master.objects.get(employee_number=request.session.get('employee_number'))
    employee_number = request.GET.get('employee_number')

    if not employee_number:
        messages.error(request, "社員番号が指定されていません。")
        return render(request, 'edit_timestamp.html', {'form': None})  # フォームなしでページに留まる

    try:
        employee = User_Master.objects.get(employee_number=employee_number)
    except User_Master.DoesNotExist:
        messages.error(request, '該当する社員が見つかりません。')
        return render(request, 'edit_timestamp.html', {'form': None})  # フォームなしでページに留まる

    # 自分自身の勤怠情報を編集しようとしているか確認
    is_self = (manager.employee_number == employee.employee_number)

    # マネージャー以上か確認
    is_manager = manager.position in ['マネージャー', '課長', '部長', '取締役', '社長']

    # 編集対象が上長か確認
    position_hierarchy = ['社員', 'リーダー', 'マネージャー', '課長', '部長', '取締役', '社長']
    manager_position_index = position_hierarchy.index(manager.position)
    employee_position_index = position_hierarchy.index(employee.position)
    
    is_superior = (employee_position_index > manager_position_index)

    if is_superior and not is_self:
        messages.error(request, 'この社員の勤怠情報を編集する権限がありません。')
        return render(request, 'edit_timestamp.html', {'form': None})  # ページに留まる

    # 勤怠情報を取得
    timestamp = TimeStamp.objects.filter(user=employee).order_by('-clock_in_time').first()

    if request.method == 'POST':
        form = TimeStampEditForm(request.POST, instance=timestamp, is_self=is_self, is_manager=is_manager)
        if form.is_valid():
            form.save()
            messages.success(request, '勤怠情報が更新されました。')
            return redirect('topPage')
    else:
        form = TimeStampEditForm(instance=timestamp, is_self=is_self, is_manager=is_manager)

    context = {
        'form': form,
        'employee': employee,
        'timestamp': timestamp,
        'is_self': is_self,
    }
    return render(request, 'edit_timestamp.html', context)
