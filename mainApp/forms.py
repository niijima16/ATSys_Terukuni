# from django import forms
# from django.forms import inlineformset_factory
# from .models import User_Master, COMPANY

# class UserMasterForm(forms.ModelForm):
#     class Meta:
#         model = User_Master
#         fields = ['account_id', 'password', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position']

# UserMasterFormSet = inlineformset_factory(COMPANY, User_Master, form=UserMasterForm, fields=['account_id', 'password', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position'], extra=1)


from django import forms
from .models import User_Master

class LoginForm(forms.Form):
    user = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)