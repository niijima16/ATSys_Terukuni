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
from mainApp import views


"""
画面遷移図､URL集:
https://docs.google.com/document/d/1GoGZs8twXaYwMq4uEY6W7ryWamZTpWFlzd0VrIR81fs/edit
"""
urlpatterns = [
    path('TerukuniAdmin/', admin.site.urls),
    path('homePage/', views.homePage, name='homePage'),
    path('register/', views.registerPage, name='registerPage'),
    path('topPage/', views.topPage, name='topPage'),
    path('upload_shifts/', views.upload_shifts, name='upload_shifts'),
    path('logout/', views.logout, name='logout'),
    path('apply_leave/', views.apply_leave, name='apply_leave'),
]