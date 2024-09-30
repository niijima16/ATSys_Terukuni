"""
URL configuration for ATSys project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainApp.views.auth_views import homePage, topPage, logout
from mainApp.views.employee_views import registerPage, edit_employee
from mainApp.views.attendance_views import edit_timestamp
from mainApp.views.leave_views import apply_leave, leave_requests, approve_leave
from mainApp.views.shift_views import upload_shifts


"""
画面遷移図､URL集:
https://docs.google.com/document/d/1GoGZs8twXaYwMq4uEY6W7ryWamZTpWFlzd0VrIR81fs/edit
"""
urlpatterns = [
    path('TerukuniAdmin/', admin.site.urls),
    path('homePage/', homePage, name='homePage'),
    path('register/', registerPage, name='registerPage'),
    path('topPage/', topPage, name='topPage'),
    path('upload_shifts/', upload_shifts, name='upload_shifts'),
    path('logout/', logout, name='logout'),
    path('apply_leave/', apply_leave, name='apply_leave'),
    path('leave_requests/', leave_requests, name='leave_requests'),
    path('approve_leave/<int:leave_request_id>/', approve_leave, name='approve_leave'),
    path('edit_employee/', edit_employee, name='edit_employee'),
    path('edit_timestamp/', edit_timestamp, name='edit_timestamp'),
]