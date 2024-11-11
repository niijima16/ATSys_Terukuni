from django.test import TestCase
from django.urls import reverse

class HomePageTests(TestCase):
    """
    ホームページのレスポンスやテンプレートの正しさを検証するテストケース。
    """

    def test_home_page_status_code(self):
        """
        ホームページが正常に200ステータスコードを返すかを確認するテスト。
        これはページが正しく読み込まれていることを示す。
        """
        response = self.client.get(reverse('homePage'))
        self.assertEqual(response.status_code, 200)

    def test_home_page_template_used(self):
        """
        ホームページが正しいテンプレート('HomePage.html')を使用しているかを確認するテスト。
        大文字と小文字を区別するので、テンプレート名が一致することが重要。
        """
        response = self.client.get(reverse('homePage'))
        self.assertTemplateUsed(response, 'HomePage.html')  # テンプレート名を確認

    def test_home_page_content(self):
        """
        ホームページに必要なコンテンツが含まれているかを確認するテスト。
        "ログイン", "新規社員アカウント登録", "パスワードをお忘れですか？"などの
        UI要素が正しく表示されているかをチェックする。
        """
        response = self.client.get(reverse('homePage'))
        self.assertContains(response, "ログイン")  # ログイン見出しの確認
        self.assertContains(response, "新規社員アカウント登録")  # 登録リンクの確認
        self.assertContains(response, "パスワードをお忘れですか？")  # パスワード忘れ案内の確認
