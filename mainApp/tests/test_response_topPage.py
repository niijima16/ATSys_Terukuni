import hashlib
from django.test import TestCase
from django.urls import reverse
from mainApp.models import User_Master

class TopPageTests(TestCase):
    """
    トップページのレスポンスやコンテンツの表示を検証するテストケース。
    """

    def setUp(self):
        """
        テストの準備としてカスタマイズしたユーザーを作成する。
        """
        # User_Masterモデルのユーザー作成
        self.user = User_Master.objects.create(
            account_id='test01@test.com',  # ログイン用のID
            password=hashlib.sha256('asdqwe'.encode()).hexdigest(),  # フロントエンドでのハッシュ化を再現
            name='Test User',
            age=30,
            gender='M',
            phone_number='1234567890',
            joined='2023-01-01',
            department_name='開発部',
            position='社員'
        )

    def login_and_set_session(self):
        """
        ログインとセッションの設定を行い、カスタムデコレーターが要求する状態にする。
        """
        # フロントエンドと同じハッシュ化方式でパスワードをハッシュ化
        hashed_password = hashlib.sha256('asdqwe'.encode()).hexdigest()

        # ログインリクエストを送信
        login_url = reverse('homePage')
        response = self.client.post(login_url, {
            'account_id': 'test01@test.com',
            'password': hashed_password
        })
        
        # セッションにemployee_numberを設定
        session = self.client.session
        session['employee_number'] = self.user.employee_number
        session.save()

    def test_login_and_access_top_page(self):
        """
        homePage.htmlでログインを行い、topPageにアクセスできるかを確認するテスト。
        """
        # ログインとセッションの設定
        self.login_and_set_session()

        # topPageへのアクセスを確認
        response = self.client.get(reverse('topPage'))
        self.assertEqual(response.status_code, 200)

    def test_top_page_template_used(self):
        """
        トップページが正しいテンプレート('topPage.html')を使用しているかを確認するテスト。
        """
        # ログインとセッションの設定
        self.login_and_set_session()

        # topPageへのアクセスを確認
        response = self.client.get(reverse('topPage'))
        self.assertTemplateUsed(response, 'topPage.html')

    def test_top_page_content(self):
        """
        トップページに必要なコンテンツが含まれているかを確認するテスト。
        "トップページ"や"勤務時間"などのUI要素が正しく表示されているかをチェックする。
        """
        # ログインとセッションの設定
        self.login_and_set_session()

        # topPageへのアクセスを確認
        response = self.client.get(reverse('topPage'))
        self.assertContains(response, "トップページ")
        self.assertContains(response, "今日の勤務時間")
        self.assertContains(response, "残り有給日数")
        self.assertContains(response, "出勤")
        self.assertContains(response, "退勤")
