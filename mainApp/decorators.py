# decorators.py

from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from .models import User_Master

# カスタム認証をチェックするデコレーター
def custom_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if 'employee_number' not in request.session:
            return redirect('homePage')  # ログインしていない場合、ログインページにリダイレクト
        return view_func(request, *args, **kwargs)
    return wrapper

# 編集権限判断用デコレーター
def manager_required(view_func):
    def wrapper(request, *args, **kwargs):
        employee_number = request.session.get('employee_number')
        if not employee_number:
            return redirect('homePage')

        user = User_Master.objects.get(employee_number=employee_number)

        # マネージャー以上の役職リスト
        manager_positions = ['マネージャー', '課長', '部長', '取締役', '社長']

        # ユーザーがマネージャー以上かをチェック
        if user.position not in manager_positions:
            raise PermissionDenied("この操作を行う権限がありません。")

        return view_func(request, *args, **kwargs)
    return wrapper
