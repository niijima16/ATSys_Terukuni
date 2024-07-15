from django import forms
from .models import User_Master

class LoginForm(forms.Form):
    user = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput)