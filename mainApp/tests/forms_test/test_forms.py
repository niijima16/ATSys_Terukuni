from django.test import TestCase
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from mainApp.forms import (
    RegisterForm, LoginForm, ShiftUploadForm, LeaveRequestForm, ApproveLeaveForm, EmployeeEditForm, TimeStampEditForm
)
from mainApp.models import User_Master, LeaveRequest, TimeStamp
from io import BytesIO

class FormsTestCase(TestCase):

    def setUp(self):
        self.user = User_Master.objects.create(
            account_id='testuser@example.com',
            password='SecurePassword123!',
            name='Test User',
            age=30,
            gender='M',
            phone_number='1234567890',
            joined=timezone.now().date(),
            department_name='Test Department',
            position='社員'
        )
        
    def test_register_form_valid(self):
        form_data = {
            'account_id': 'newuser@example.com',  # Updated to a valid email address
            'password': 'SecurePassword123!',
            'name': 'New User',
            'age': 25,
            'gender': 'F',
            'phone_number': '0987654321',
            'joined': timezone.now().date(),
            'department_name': 'Test Department',
            'position': '社員'  # Updated to valid choice
        }
        form = RegisterForm(data=form_data)
        if not form.is_valid():
            self.fail(f"RegisterForm validation failed: {form.errors}")
        self.assertTrue(form.is_valid())

    def test_login_form_valid(self):
        form_data = {
            'user_id': 'testuser',
            'password': 'SecurePassword123!'
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_shift_upload_form_valid(self):
        form_data = {}
        file_mock = SimpleUploadedFile('dummy.csv', b"dummy data for csv", content_type='text/csv')  # Use SimpleUploadedFile for testing
        form = ShiftUploadForm(data=form_data, files={'csv_file': file_mock})
        if not form.is_valid():
            self.fail(f"ShiftUploadForm validation failed: {form.errors}")
        self.assertTrue(form.is_valid())

    def test_leave_request_form_invalid_dates(self):
        form_data = {
            'leave_type': 1,  # Assuming `leave_type` is a ForeignKey or ChoiceField that expects an integer
            'start_date': timezone.now().date(),
            'end_date': timezone.now().date() - timezone.timedelta(days=1),
            'applicant_comment': 'Need leave'
        }
        form = LeaveRequestForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)

    def test_employee_edit_form_self_edit(self):
        form = EmployeeEditForm(instance=self.user, is_self=True)
        self.assertTrue(form.fields['account_id'].disabled)
        self.assertTrue(form.fields['joined'].disabled)
        self.assertTrue(form.fields['department_name'].disabled)
        self.assertTrue(form.fields['position'].disabled)

    def test_employee_edit_form_superior_edit(self):
        form = EmployeeEditForm(instance=self.user, is_superior=True)
        self.assertTrue(form.fields['account_id'].disabled)
        self.assertTrue(form.fields['joined'].disabled)
        self.assertTrue(form.fields['department_name'].disabled)
        self.assertTrue(form.fields['position'].disabled)

    def test_timestamp_edit_form_self_edit(self):
        timestamp = TimeStamp.objects.create(
            user=self.user,
            clock_in_time=timezone.now(),
            clock_out_time=timezone.now() + timezone.timedelta(hours=8)
        )
        form = TimeStampEditForm(instance=timestamp, is_self=True)
        self.assertTrue(form.fields['clock_in_time'].disabled)
        self.assertTrue(form.fields['clock_out_time'].disabled)

    def test_timestamp_edit_form_manager_edit(self):
        timestamp = TimeStamp.objects.create(
            user=self.user,
            clock_in_time=timezone.now(),
            clock_out_time=timezone.now() + timezone.timedelta(hours=8)
        )
        form = TimeStampEditForm(instance=timestamp, is_manager=True)
        self.assertFalse(form.fields['clock_in_time'].disabled)
        self.assertFalse(form.fields['clock_out_time'].disabled)
