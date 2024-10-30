from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.core.exceptions import PermissionDenied
from mainApp.models import User_Master  # User_Master モデルのインポート
from mainApp.decorators import custom_login_required, manager_required  # デコレーターのインポート
from django.contrib.sessions.middleware import SessionMiddleware

class TestAuthDecorators(TestCase):
    """カスタム認証デコレーターの動作を検証するためのテストクラス"""

    def setUp(self):
        """
        各テストの前に実行される初期化メソッド。
        テスト用のユーザーを作成し、RequestFactoryをセットアップする。
        """
        # RequestFactory はDjangoのテスト用リクエスト生成ツール
        self.factory = RequestFactory()

        # テスト用ユーザーの作成（役職は「マネージャー」）
        self.user = User_Master.objects.create(
            account_id='manager@example.com',
            password='password123',  # テスト環境では暗号化不要
            name='Manager User',
            age=35,
            gender='M',
            phone_number='08012345678',
            joined='2023-01-01',
            department_name='営業部',
            position='マネージャー'
        )

    def _setup_session(self, request):
        """
        リクエストにセッションを設定するヘルパーメソッド。
        DjangoのRequestFactoryではセッションが使えないため、
        SessionMiddlewareを通してセッションを有効化する。
        """
        # ダミーの get_response 関数を渡して SessionMiddleware を初期化
        middleware = SessionMiddleware(lambda request: None)
        middleware.process_request(request)  # リクエストにセッションをバインド
        request.session.save()  # セッションを保存

    def test_custom_login_required_authenticated(self):
        """セッションに社員番号がある場合、対象ビューが正常に呼び出されることを確認する。"""
        request = self.factory.get('/some-url/')
        self._setup_session(request)  # セッションをセットアップ
        request.session['employee_number'] = self.user.employee_number  # 社員番号をセッションに追加

        @custom_login_required
        def sample_view(request):
            return 'Success'  # テスト対象のダミービュー

        response = sample_view(request)  # デコレーター付きビューの実行
        self.assertEqual(response, 'Success')  # 正常に呼び出されたか確認

    def test_custom_login_required_unauthenticated(self):
        """セッションに社員番号がない場合、ログインページにリダイレクトされることを確認する。"""
        request = self.factory.get('/some-url/')
        self._setup_session(request)  # セッションをセットアップ

        @custom_login_required
        def sample_view(request):
            return 'Success'  # テスト対象のダミービュー

        response = sample_view(request)  # デコレーター付きビューの実行
        self.assertEqual(response.status_code, 302)  # リダイレクト確認
        self.assertEqual(response.url, reverse('homePage'))  # ログインページへのリダイレクト確認

    def test_manager_required_authorized(self):
        """ユーザーがマネージャー以上の場合、対象ビューが正常に呼び出されることを確認する。"""
        request = self.factory.get('/some-url/')
        self._setup_session(request)  # セッションをセットアップ
        request.session['employee_number'] = self.user.employee_number  # 社員番号をセッションに追加

        @manager_required
        def sample_view(request):
            return 'Success'  # テスト対象のダミービュー

        response = sample_view(request)  # デコレーター付きビューの実行
        self.assertEqual(response, 'Success')  # 正常に呼び出されたか確認

    def test_manager_required_unauthorized(self):
        """ユーザーがマネージャー未満の場合、PermissionDeniedが発生することを確認する。"""
        # 役職を「社員」に変更（マネージャー未満のユーザーにする）
        self.user.position = '社員'
        self.user.save()

        request = self.factory.get('/some-url/')
        self._setup_session(request)  # セッションをセットアップ
        request.session['employee_number'] = self.user.employee_number  # 社員番号をセッションに追加

        @manager_required
        def sample_view(request):
            return 'Success'  # テスト対象のダミービュー

        # PermissionDenied 例外が発生することを確認
        with self.assertRaises(PermissionDenied):
            sample_view(request)  # デコレーター付きビューの実行
