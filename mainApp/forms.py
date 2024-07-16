from django import forms
from .models import User_Master

class LoginForm(forms.Form):
    user = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User_Master
        fields = ['account_id', 'password', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position', 'company']
        widgets = {
            'password': forms.PasswordInput(),
            'joined': forms.DateInput(attrs={'type': 'date'}),
        }