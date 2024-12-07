# mainApp/views/leave_views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from mainApp.models import User_Master, LeaveRequest, PaidLeave
from mainApp.forms import LeaveRequestForm, ApproveLeaveForm
from mainApp.decorators import custom_login_required

# 有給申請用
def apply_leave(request):
    employee_number = request.session.get('employee_number')
    if not employee_number:
        return redirect('homePage')

    user = get_object_or_404(User_Master, employee_number=employee_number)

    # フォームを初期化
    form = LeaveRequestForm()

    if request.method == 'POST':
        if 'withdraw' in request.POST:  # 取り下げボタンが押された場合
            leave_request_id = request.POST.get('leave_request_id')
            leave_request = get_object_or_404(LeaveRequest, id=leave_request_id, user=user)

            if leave_request.approved:
                messages.error(request, '承認済みの申請は取り下げできません。')
            else:
                leave_request.delete()
                messages.success(request, '申請を取り下げました。')

        else:  # 新規申請の場合
            form = LeaveRequestForm(request.POST)
            if form.is_valid():
                leave_request = form.save(commit=False)
                leave_request.user = user
                leave_request.applicant_comment = form.cleaned_data.get('applicant_comment')

                if leave_request.leave_type == 'Paid':
                    paid_leave = PaidLeave.objects.get(user=user)
                    requested_days = (leave_request.end_date - leave_request.start_date).days + 1

                    if requested_days > paid_leave.remaining_days:
                        messages.error(request, '申請日数が残り有給日数を超えています。')
                        return render(request, 'apply_leave.html', {'form': form, 'pending_requests': pending_requests})

                    try:
                        paid_leave.use_leave(requested_days)
                    except ValueError as e:
                        messages.error(request, str(e))
                        return render(request, 'apply_leave.html', {'form': form, 'pending_requests': pending_requests})

                leave_request.approved = False
                leave_request.save()
                messages.success(request, '有給申請が正常に送信されました。')

    # 未承認の申請を取得
    pending_requests = LeaveRequest.objects.filter(user=user, approved=False)

    return render(request, 'apply_leave.html', {'form': form, 'pending_requests': pending_requests})

# 承認時のコメント機能
def approve_leave(request, leave_request_id):
    employee_number = request.session.get('employee_number')
    if not employee_number:
        return redirect('homePage')

    approver = get_object_or_404(User_Master, employee_number=employee_number)
    leave_request = get_object_or_404(LeaveRequest, id=leave_request_id)

    # 承認者が申請者の上司でない場合、承認/却下できない
    if approver not in leave_request.user.get_superiors():
        messages.error(request, '承認権限がありません。')
        return redirect('leave_requests')

    if request.method == 'POST':
        if 'approve' in request.POST:  # 承認ボタンが押された場合
            form = ApproveLeaveForm(request.POST, instance=leave_request)
            if form.is_valid():
                leave_request = form.save(commit=False)
                leave_request.approved = True
                leave_request.save()
                messages.success(request, '有給申請を承認しました。')
                return redirect('leave_requests')

        elif 'reject' in request.POST:  # 却下ボタンが押された場合
            leave_request.approved = False
            leave_request.approver_comment = request.POST.get('approver_comment', '')
            leave_request.save()
            messages.warning(request, '有給申請を却下しました。')
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
    if not employee_number:
        return redirect('homePage')

    user = get_object_or_404(User_Master, employee_number=employee_number)

    # 承認が必要な申請のみ取得（却下済みは除外）
    leave_requests = LeaveRequest.objects.filter(
        approved=False,
        approver_comment__isnull=True  # 却下されたものを除外
    )

    context = {
        'leave_requests': leave_requests,
    }
    return render(request, 'leave_requests.html', context)
