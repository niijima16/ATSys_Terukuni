from django.contrib import admin
from mainApp.models.user_master import User_Master
from mainApp.models.leave_type import LeaveType
from mainApp.models.time_sheet import TimeSheet
from mainApp.models.time_shift import Shift
from mainApp.models.leave_request import LeaveRequest

@admin.register(User_Master) # ユーザー情報テーブル
class UserMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_id', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position')
    search_fields = ('name', 'account_id', 'phone_number')
    list_filter = ('gender', 'position')

@admin.register(LeaveType) # 休暇種類テーブル
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TimeSheet) # タイムシートテーブル
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'break_time', 'overtime', 'leave_type', 'comments')
    search_fields = ('user__username', 'date')
    list_filter = ('leave_type',)
    
@admin.register(Shift)  # シフトモデルの管理
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time', 'break_time', 'shift_type')
    search_fields = ('user__name', 'date')
    list_filter = ('shift_type',)
    
@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'leave_type', 'start_date', 'end_date', 'approved')
    search_fields = ('user__name', 'leave_type__name', 'start_date', 'end_date')
    list_filter = ('leave_type', 'approved')