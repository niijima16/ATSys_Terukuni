from django.contrib import admin
from mainApp.models.user_master import User_Master
from mainApp.models.leave_type import LeaveType
from mainApp.models.time_stamp import TimeStamp
from mainApp.models.time_shift import Shift
from mainApp.models.leave_request import LeaveRequest

@admin.register(User_Master)  # ユーザー情報テーブル
class UserMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'account_id', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position')
    search_fields = ('name', 'account_id', 'phone_number')
    list_filter = ('gender', 'position')

@admin.register(LeaveType)  # 休暇種類テーブル
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TimeStamp)  # 打刻情報テーブル
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'clock_in_time', 'clock_out_time')
    list_filter = ('user',)

    def worked_hours(self, obj):
        return obj.calculate_worked_hours()
    worked_hours.short_description = 'Worked Hours'

    # worked_hoursを表示に追加する場合
    list_display += ('worked_hours',)

@admin.register(Shift)  # シフト情報テーブル
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'weekday', 'start_time', 'end_time', 'is_weekend')
    list_filter = ('user', 'date', 'is_weekend')
    search_fields = ('user__name', 'date', 'weekday')

@admin.register(LeaveRequest)  # 休暇申請テーブル
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'leave_type', 'start_date', 'end_date', 'approved')
    search_fields = ('user__name', 'leave_type__name', 'start_date', 'end_date')
    list_filter = ('leave_type', 'approved')