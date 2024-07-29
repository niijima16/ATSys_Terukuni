from django.test import TestCase
from mainApp.models import User_Master

class UserMasterTestCase(TestCase):
    def test_create_user_master(self):
        user = User_Master.objects.create(
            account_id='test@example.com',
            password='password',
            name='Test User',
            age=30,
            gender='M',
            phone_number='12345678901',
            joined='2024-01-01',
            department_name='Test Department',
            position='マネージャー'
        )
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.account_id, 'test@example.com')
        self.assertEqual(user.position, 'マネージャー')