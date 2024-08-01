from django.shortcuts import render, redirect
from django.utils import timezone
from .models import User_Master, TimeSheet
from .forms import LoginForm, RegisterForm

def homePage(request):
    error_message = None
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['user_id']
            password = form.cleaned_data['password']
            try:
                user = User_Master.objects.get(account_id=account)
                if password == user.password:
                    request.session['user_name'] = user.name  # セッションにユーザー名を保存
                    return redirect('topPage')
                else:
                    error_message = 'パスワードが正しくありません。'
            except User_Master.DoesNotExist:
                error_message = 'アカウントが見つかりません。'
    else:
        form = LoginForm()

    return render(request, 'HomePage.html', {'form': form, 'error_message': error_message})

def topPage(request):
    user_name = request.session.get('user_name', 'ゲスト')  # セッションからユーザー名を取得
    user = User_Master.objects.get(name=user_name)
    if request.method == 'POST' :
        if 'clock_in' in request.POST: # 出金処理
            TimeSheet.objects.create(
                user = user,
                data = timezone.now().date(),
                start_time = timezone.now().time()
            )
        elif 'clock_out' in request.POST: # 退勤処理
            try:
                timesheet = TimeSheet.objects.filter(user=user, date=timezone.now().date()).latest('start_time')
                timesheet.end_time = timezone.now().time()
                timesheet.save()
            except TimeSheet.DoesNotExist:
                pass
        return redirect('topPage')
    
    return render(request, 'topPage.html', {'user_name': user_name})

def registerPage(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('homePage')
    else:
        form = RegisterForm()
    return render(request, 'Registration.html', {'form': form})