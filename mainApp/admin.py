from django.contrib import admin
from mainApp.models.user_master import User_Master
from mainApp.models.leave_type import LeaveType
from mainApp.models.time_stamp import TimeStamp
from mainApp.models.time_shift import Shift
from mainApp.models.leave_request import LeaveRequest
from mainApp.models.paid_leave import PaidLeave


@admin.register(User_Master)
class UserMasterAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'name', 'account_id', 'age', 'gender', 'phone_number', 'joined', 'department_name', 'position')
    search_fields = ('employee_number', 'name', 'account_id', 'phone_number')
    list_filter = ('gender', 'position')

@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(TimeStamp)
class TimeSheetAdmin(admin.ModelAdmin):
    list_display = ('user', 'clock_in_time', 'clock_out_time', 'worked_hours')
    list_filter = ('user',)

    def worked_hours(self, obj):
        return obj.calculate_worked_hours()
    worked_hours.short_description = 'Worked Hours'

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('get_employee_number', 'user', 'date', 'weekday', 'start_time', 'end_time', 'is_weekend')
    list_filter = ('user', 'date', 'is_weekend')
    search_fields = ('user__name', 'date', 'weekday')

    def get_employee_number(self, obj):
        return obj.user.employee_number
    get_employee_number.short_description = 'Employee Number'
    
admin.site.register(PaidLeave)
admin.site.register(LeaveRequest)