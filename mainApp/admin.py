from django.contrib import admin

from mainApp.models.user_master import User_Master

from mainApp.models.company import COMPANY

# Register your models here.
admin.site.register(User_Master)

admin.site.register(COMPANY)