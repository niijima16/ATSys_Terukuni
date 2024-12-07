# mainApp/forms.py

from django import forms
from .models import User_Master, LeaveRequest, TimeStamp

# 登録用forms(ヒント付き)
class RegisterForm(forms.ModelForm):
    class Meta:
        model = User_Master
        fields = ['account_id', 'password', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position']
        widgets = {
            'account_id': forms.TextInput(attrs={
                'placeholder': '例: tanaka@levels.com',
                'class': 'form-control'
            }),
            'password': forms.PasswordInput(attrs={
                'placeholder': '8文字以上のパスワード',
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'placeholder': '例: 山田 太郎',
                'class': 'form-control'
            }),
            'age': forms.NumberInput(attrs={
                'placeholder': '例: 30',
                'class': 'form-control'
            }),
            'gender': forms.Select(attrs={
                'class': 'form-control'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': '例: 090-1234-5678',
                'class': 'form-control'
            }),
            'joined': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'department_name': forms.TextInput(attrs={
                'placeholder': '例: 営業部',
                'class': 'form-control'
            }),
            'position': forms.TextInput(attrs={
                'placeholder': '例: マネージャー',
                'class': 'form-control'
            }),
        }

# ログイン用
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
        
# 情報編集フォーム
class EmployeeEditForm(forms.ModelForm):
    class Meta:
        model = User_Master
        fields = ['account_id', 'name', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position']

    def __init__(self, *args, **kwargs):
        is_manager = kwargs.pop('is_manager', False)
        is_self = kwargs.pop('is_self', False)
        is_superior = kwargs.pop('is_superior', False)
        super(EmployeeEditForm, self).__init__(*args, **kwargs)

        # 自分自身を編集する場合、常に特定フィールドを無効にする
        if is_self:
            self.fields['account_id'].disabled = True
            self.fields['joined'].disabled = True
            self.fields['department_name'].disabled = True
            self.fields['position'].disabled = True

        # 上長を編集している場合、特定フィールドを無効にする
        elif is_superior:
            self.fields['account_id'].disabled = True
            self.fields['joined'].disabled = True
            self.fields['department_name'].disabled = True
            self.fields['position'].disabled = True
            
# 勤務時間編集フォーム
class TimeStampEditForm(forms.ModelForm):
    class Meta:
        model = TimeStamp
        fields = ['clock_in_time', 'clock_out_time']

    def __init__(self, *args, **kwargs):
        is_manager = kwargs.pop('is_manager', False)
        is_self = kwargs.pop('is_self', False)
        super(TimeStampEditForm, self).__init__(*args, **kwargs)

        # 自分自身の勤務時間を編集できないようにする
        if is_self:
            self.fields['clock_in_time'].disabled = True
            self.fields['clock_out_time'].disabled = True

        # 管理者以外は勤務時間を編集できない
        if not is_manager:
            self.fields['clock_in_time'].disabled = True
            self.fields['clock_out_time'].disabled = True