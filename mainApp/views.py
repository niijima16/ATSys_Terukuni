# from django.shortcuts import render, redirect
# from django.contrib.auth.hashers import check_password
# from .models import User_Master, COMPANY
# from .forms import UserMasterFormSet

# def homePage(request):
#     error_message = None
#     formset = UserMasterFormSet(instance=COMPANY())  # フォームセットを初期化

#     if request.method == 'POST':
#         # ログイン認証
#         account = request.POST.get('user')
#         password = request.POST.get('password')
        
#         if account == 'root@levels.co.jp' and check_password(password, 'root'):
#             # 認証成功時の処理
#             formset = UserMasterFormSet(request.POST, instance=COMPANY())  # 親オブジェクトのインスタンスをフォームセットに渡す
#             if formset.is_valid():
#                 formset.save()
#                 return redirect('topPage')  # urlpatternsで定義した'topPage'という名前のビューにリダイレクトする
#         else:
#             # 認証失敗時の処理
#             error_message = 'ログインに失敗しました。有効なアカウント情報を入力してください。'

#     return render(request, 'HomePage.html', {
#         'formset': formset,
#         'error_message': error_message,
#     })

# def topPage(request):
#     return render(request, 'topPage.html')

# test01@levels.co.jp
# test01　


from django.shortcuts import render, redirect
from .models import User_Master
from .forms import LoginForm

def homePage(request):
    error_message = None

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data['user']
            password = form.cleaned_data['password']
            try:
                user = User_Master.objects.get(account_id=account)
                if password == user.password:
                    return redirect('topPage')
                else:
                    error_message = 'パスワードが正しくありません。'
            except User_Master.DoesNotExist:
                error_message = 'アカウントが見つかりません。'
    else:
        form = LoginForm()

    return render(request, 'HomePage.html', {'form': form, 'error_message': error_message})

def topPage(request):
    return render(request, 'topPage.html')