# tests/models/test_user_master.py

from django.test import TestCase
from mainApp.models.user_master import User_Master
from datetime import date
from django.db import IntegrityError

class UserMasterModelTest(TestCase):

    def setUp(self):
        # テスト用のデータを作成
        self.user1 = User_Master.objects.create(
            account_id='user1@example.com',
            password='password123',
            name='Taro Yamada',
            age=30,
            gender='M',
            phone_number='09012345678',
            joined=date(2020, 1, 15),
            department_name='Sales',
            position='社員'
        )
        self.user2 = User_Master.objects.create(
            account_id='user2@example.com',
            password='password123',
            name='Hanako Suzuki',
            age=28,
            gender='F',
            phone_number='08012345679',
            joined=date(2021, 6, 1),
            department_name='HR',
            position='課長'
        )

    def test_user_creation(self):
        # 作成したユーザーが期待通りの属性を持っているかテスト
        self.assertEqual(self.user1.account_id, 'user1@example.com')
        self.assertEqual(self.user1.name, 'Taro Yamada')
        self.assertEqual(self.user1.position, '社員')
        self.assertIsNotNone(self.user1.user_id)
        self.assertIsNotNone(self.user1.employee_number)

    def test_str_method(self):
        # __str__ メソッドが正しいフォーマットで返すかをテスト
        self.assertEqual(str(self.user1), f"Taro Yamada - {self.user1.employee_number}")

    def test_user_id_auto_increment(self):
        # user_idが自動的にインクリメントされているかをテスト
        self.assertEqual(self.user1.user_id, 1)
        self.assertEqual(self.user2.user_id, 2)

    def test_employee_number_auto_increment(self):
        # employee_numberが自動的に設定されているかをテスト
        self.assertEqual(self.user1.employee_number, 10000000)
        self.assertEqual(self.user2.employee_number, 10000001)

    def test_get_superiors(self):
        # get_superiorsメソッドが期待通りの上長を返すかをテスト
        superiors = self.user1.get_superiors()
        self.assertIn(self.user2, superiors)
        self.assertEqual(superiors.count(), 1)

        # 課長のユーザーにはそれ以上の役職者がいないため、空のクエリセットが返ることを確認
        superiors_of_user2 = self.user2.get_superiors()
        self.assertEqual(superiors_of_user2.count(), 0)

    def test_field_constraints(self):
        # ユニーク制約のテスト
        with self.assertRaises(IntegrityError):
            User_Master.objects.create(
                account_id='user1@example.com',  # 同じaccount_idのユーザーはエラーになるはず
                password='password123',
                name='Duplicate User',
                age=25,
                gender='M',
                phone_number='07012345678',
                joined=date(2022, 1, 1),
                department_name='IT',
                position='社員'
            )