from django.test import TestCase
from models.user_master import User_Master

class UserMasterTestCase(TestCase):
    def test_create_user_master(self):
        user = User_Master.objects.create(
            account_id="test01@test.com",
            password="testpassword",
            name="Test User",
            age=30,
            gender="M",
            phone_number="12345678901",
            joined="2023-07-01",
            department_name="Test Department",
            position="マネージャー",
            company_id=1  # 適切な会社IDを設定してください
        )

        self.assertEqual(User_Master.objects.count(), 1)
        self.assertEqual(user.account_id, "test01@test.com")
        self.assertEqual(user.name, "Test User")
        self.assertEqual(user.position, "マネージャー")