# mainApp/views/leave_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from mainApp.models import User_Master, LeaveRequest, PaidLeave
from mainApp.forms import LeaveRequestForm, ApproveLeaveForm
from mainApp.decorators import custom_login_required

# 有給申請用
def apply_leave(request):
    employee_number = request.session.get('employee_number')  # セッションからemployee_numberを取得
    if not employee_number:
        return redirect('homePage')  # セッションが無効な場合はログインページにリダイレクト

    user = get_object_or_404(User_Master, employee_number=employee_number)

    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.user = user
            leave_request.applicant_comment = form.cleaned_data.get('applicant_comment')

            # 有給残日数のチェック
            if leave_request.leave_type == 'Paid':
                paid_leave = PaidLeave.objects.get(user=user)
                requested_days = (leave_request.end_date - leave_request.start_date).days + 1

                if requested_days > paid_leave.remaining_days:
                    messages.error(request, '申請日数が残り有給日数を超えています。')
                    return render(request, 'apply_leave.html', {'form': form})

                # 残り有給日数の更新
                try:
                    paid_leave.use_leave(requested_days)
                except ValueError as e:
                    messages.error(request, str(e))
                    return render(request, 'apply_leave.html', {'form': form})

            leave_request.approved = False  # 初期状態で申請は未承認
            leave_request.save()
            messages.success(request, '有給申請が正常に送信されました。')
            return redirect('topPage')
    else:
        form = LeaveRequestForm()

    return render(request, 'apply_leave.html', {'form': form})

# 承認時のコメント機能
def approve_leave(request, leave_request_id):
    employee_number = request.session.get('employee_number')  # セッションからemployee_numberを取得
    if not employee_number:
        return redirect('homePage')  # セッションが無効な場合はログインページにリダイレクト

    # 承認者と申請を取得
    approver = get_object_or_404(User_Master, employee_number=employee_number)
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    # 取締役と社長は承認できない
    if approver.position in ['取締役', '社長']:
        messages.error(request, '取締役と社長は承認できません。')
        return redirect('leave_requests')  # リストに戻る

    # 承認者が申請者の上司でない場合、承認できない
    if approver not in leave_request.user.get_superiors():
        messages.error(request, '承認権限がありません。')
        return redirect('leave_requests')  # リストに戻る

    # POSTリクエストの場合、承認処理を実行
    if request.method == 'POST':
        form = ApproveLeaveForm(request.POST, instance=leave_request)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.approved = True
            leave_request.save()
            messages.success(request, '有給申請を承認しました。')
            return redirect('leave_requests')
    else:
        form = ApproveLeaveForm(instance=leave_request)

    context = {
        'leave_request': leave_request,
        'form': form,
    }
    return render(request, 'approve_leave.html', context)

# 承認者リスト
@custom_login_required
def leave_requests(request):
    employee_number = request.session.get('employee_number')
    user = get_object_or_404(User_Master, employee_number=employee_number)

    # リーダー以上のユーザーのみがアクセスできる
    if user.position not in ['リーダー','マネージャー', '課長', '部長']:
        return redirect('homePage')

    # 未承認の申請のみ表示
    leave_requests = LeaveRequest.objects.filter(approved=False)

    context = {
        'leave_requests': leave_requests
    }
    return render(request, 'leave_requests.html', context)
