# context_processors.py

from .models import User_Master

def user_info(request):
    """
    ユーザー情報をテンプレートで使用するためのコンテキストプロセッサ。
    """
    employee_number = request.session.get('employee_number')
    user_name = None

    if employee_number:
        try:
            user = User_Master.objects.get(employee_number=employee_number)
            user_name = user.name
        except User_Master.DoesNotExist:
            pass

    return {
        'employee_number': employee_number,
        'user_name': user_name,
    }