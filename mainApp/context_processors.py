# context_processors.py

from .models import User_Master

def user_info(request):
    if request.session.get('employee_number'):
        try:
            user = User_Master.objects.get(employee_number=request.session.get('employee_number'))
            return {
                'employee_number': user.employee_number,
                'user_name': user.name,
                'position': user.position,
            }
        except User_Master.DoesNotExist:
            return {}
    return {}