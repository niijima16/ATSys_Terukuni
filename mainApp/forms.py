# mainApp/forms.py

from django import forms
from .models import User_Master, LeaveRequest

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User_Master
        fields = ['account_id', 'password', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position']
        widgets = {
            'password': forms.PasswordInput(),
            'joined': forms.DateInput(attrs={'type': 'date'}),
        }

class LoginForm(forms.Form):
    user_id = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())

# Shiftデータをアップロードするためのフォーム
class ShiftUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date']  # 'is_paid_leave'を削除
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }