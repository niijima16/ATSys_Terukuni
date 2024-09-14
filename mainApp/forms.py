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

# 有給申請フォーム
class LeaveRequestForm(forms.ModelForm):
    applicant_comment = forms.CharField(widget=forms.Textarea, required=False, label='申請者のコメント')

    class Meta:
        model = LeaveRequest
        fields = ['leave_type', 'start_date', 'end_date', 'applicant_comment']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("開始日は終了日よりも前である必要があります。")

        return cleaned_data

# 承認時に使用するフォーム
class ApproveLeaveForm(forms.ModelForm):
    approver_comment = forms.CharField(widget=forms.Textarea, required=False, label='承認者のコメント')  # 承認者のコメント欄を追加

    class Meta:
        model = LeaveRequest
        fields = ['approver_comment']  # 承認者のコメントフィールドのみを扱う