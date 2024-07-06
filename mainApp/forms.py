# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import COMPANY, User_Master

class CompanyForm(forms.ModelForm):
    class Meta:
        model = COMPANY
        fields = ['name', 'address', 'phone_number']  # COMPANYモデルのフィールドを定義

UserMasterFormSet = inlineformset_factory(COMPANY, User_Master, fields=['account_id', 'password', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name'], extra=1)