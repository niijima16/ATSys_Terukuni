from django.contrib import admin
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from mainApp.models.user_master import User_Master
from mainApp.models.leave_type import LeaveType
from mainApp.models.time_sheet import TimeSheet
from mainApp.models.time_shift import Shift
from mainApp.models.leave_request import LeaveRequest
from .forms import ShiftUploadForm
import pandas as pd

@admin.register(User_Master) # ユーザー情報テーブル
class UserMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_id', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position')
    search_fields = ('name', 'account_id', 'phone_number')
    list_filter = ('gender', 'position')

@admin.register(LeaveType) # 休暇種類テーブル
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TimeSheet)
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'break_time', 'overtime', 'leave_type', 'comments')
    search_fields = ('user__username', 'date')
    list_filter = ('leave_type',)

@admin.register(Shift)  # シフトテーブルの管理
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'break_time', 'shift_type')
    search_fields = ('user__name', 'date')
    list_filter = ('shift_type',)
    actions = ['import_shifts']

    def import_shifts(self, request, queryset):
        if request.method == 'POST':
            form = ShiftUploadForm(request.POST, request.FILES)
            if form.is_valid():
                excel_file = request.FILES['file']
                df = pd.read_excel(excel_file, engine='openpyxl')

                for index, row in df.iterrows():
                    try:
                        user = User_Master.objects.get(name=row['name'])
                        Shift.objects.create(
                            user=user,
                            date=row['date'],
                            start_time=row['start_time'],
                            end_time=row['end_time'],
                            break_time=row['break_time'],
                            shift_type=row['shift_type']
                        )
                    except User_Master.DoesNotExist:
                        self.message_user(request, f"User {row['name']} does not exist.", level='error')

                self.message_user(request, "Shifts imported successfully")
                return HttpResponseRedirect("..")  # 管理画面にリダイレクト

        else:
            form = ShiftUploadForm()

        return render(request, 'admin/upload_shifts.html', {'form': form})

    import_shifts.short_description = 'Import shifts from Excel'

@admin.register(LeaveRequest) # 休暇申請テーブルの管理
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'leave_type', 'start_date', 'end_date', 'approved')
    search_fields = ('user__name', 'leave_type__name', 'start_date', 'end_date')
    list_filter = ('leave_type', 'approved')