from .test_Func_user_and_login_pkg import BaseTestCase
from django.urls import reverse
from django.test import TestCase

class TopPageTests(BaseTestCase):
    """
    トップページのレスポンスやコンテンツの表示を検証するテストケース。
    """

    def test_login_and_access_top_page(self):
        """
        homePage.htmlでログインを行い、topPageにアクセスできるかを確認するテスト。
        """
        # BaseTestCaseでログインとセッションの設定が完了しているため、直接topPageへアクセス
        response = self.client.get(reverse('topPage'))
        self.assertEqual(response.status_code, 200)

    def test_top_page_template_used(self):
        """
        トップページが正しいテンプレート('topPage.html')を使用しているかを確認するテスト。
        """
        # BaseTestCaseでログインとセッションの設定が完了しているため、直接topPageへアクセス
        response = self.client.get(reverse('topPage'))
        self.assertTemplateUsed(response, 'topPage.html')

    def test_top_page_content(self):
        """
        トップページに必要なコンテンツが含まれているかを確認するテスト。
        "トップページ"や"勤務時間"などのUI要素が正しく表示されているかをチェックする。
        """
        # BaseTestCaseでログインとセッションの設定が完了しているため、直接topPageへアクセス
        response = self.client.get(reverse('topPage'))
        self.assertContains(response, "トップページ")
        self.assertContains(response, "今日の勤務時間")
        self.assertContains(response, "残り有給日数")
        self.assertContains(response, "出勤")
        self.assertContains(response, "退勤")
