# mainApp/views/employee_views.py

from django.shortcuts import render, redirect
from django.contrib import messages
from mainApp.models import User_Master
from mainApp.forms import RegisterForm, EmployeeEditForm
from mainApp.decorators import custom_login_required, manager_required
import hashlib

# 社員情報登録用
def registerPage(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # パスワードをハッシュ化して保存
            user.password = hashlib.sha256(user.password.encode()).hexdigest()
            user.save()
            messages.success(request, 'ユーザー登録が成功しました。')
            return redirect('homePage')
    else:
        form = RegisterForm()
    return render(request, 'Registration.html', {'form': form})

# 情報編集用
@custom_login_required
@manager_required
def edit_employee(request):
    manager = User_Master.objects.get(employee_number=request.session.get('employee_number'))
    employee_number = request.GET.get('employee_number')

    if not employee_number:
        messages.error(request, "社員番号が指定されていません。")
        return render(request, 'edit_employee.html', {'form': None})  # フォームがない状態でページに留まる

    try:
        employee = User_Master.objects.get(employee_number=employee_number)
    except User_Master.DoesNotExist:
        messages.error(request, '該当する社員が見つかりません。')
        return render(request, 'edit_employee.html', {'form': None})  # フォームがない状態でページに留まる

    # 自分自身を編集しようとしているか確認
    is_self = (manager.employee_number == employee.employee_number)

    # マネージャー以上か確認
    is_manager = manager.position in ['マネージャー', '課長', '部長', '取締役', '社長']

    # 編集対象が上長か確認
    position_hierarchy = ['社員', 'リーダー', 'マネージャー', '課長', '部長', '取締役', '社長']
    manager_position_index = position_hierarchy.index(manager.position)
    employee_position_index = position_hierarchy.index(employee.position)
    
    is_superior = (employee_position_index > manager_position_index)

    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee, is_self=is_self, is_manager=is_manager, is_superior=is_superior)
        if form.is_valid():
            form.save()
            messages.success(request, '社員情報が更新されました。')
            return redirect('topPage')
    else:
        form = EmployeeEditForm(instance=employee, is_self=is_self, is_manager=is_manager, is_superior=is_superior)

    context = {
        'form': form,
        'employee': employee,
        'is_self': is_self,
    }
    return render(request, 'edit_employee.html', context)
