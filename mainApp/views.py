from django.shortcuts import render,HttpResponse,redirect

# Create your views here.
def homePage(request):  # 変える予定
    if request.method == "GET":
        return render(request,"homePage.html")

    account = request.POST.get("user")
    password = request.POST.get("password")

    if account == 'root@levels.co.jp' and password == "123":
        return render(request,"topPage.html")

def topPage(request):
    return render(request,"topPage.html")
