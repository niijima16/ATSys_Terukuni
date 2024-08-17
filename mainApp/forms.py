# mainApp/forms.py
from django import forms
from .models import User_Master

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
<<<<<<< HEAD
=======
    
# # excelでシフトを読み込む
# class ShiftUploadForm(forms.Form):
#     file = forms.FileField(label='シフトファイルを選択')
>>>>>>> cedb43bdacc9c3e28a20b4d417a6f9d9e71c507f

# csvでシフトを読み込む
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(label='CSVファイルを選択')

# excelでシフトを読み込む
# class ShiftUploadForm(forms.Form):
#     file = forms.FileField(label='シフトファイルを選択')