from django.test import TestCase
from mainApp.models.leave_type import LeaveType

class LeaveTypeModelTest(TestCase):
    def test_leave_type_creation(self):
        # LeaveTypeインスタンスが正しく作成されることをテストします
        leave_type = LeaveType.objects.create(name='Annual Leave', description='Yearly paid leave')
        
        # 各フィールドが正しく保存されているかをアサート
        self.assertEqual(leave_type.name, 'Annual Leave')
        self.assertEqual(leave_type.description, 'Yearly paid leave')

    def test_string_representation(self):
        # LeaveTypeの文字列表現が正しいことをテストします
        leave_type = LeaveType.objects.create(name='Annual Leave')
        
        # __str__メソッドが正しい文字列を返すかをアサート
        self.assertEqual(str(leave_type), 'Annual Leave')
