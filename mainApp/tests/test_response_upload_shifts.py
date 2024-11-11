from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .test_Func_user_and_login_pkg import BaseTestCase

class UploadShiftsTests(BaseTestCase):
    """
    upload_shiftsページのCSVアップロード機能を検証するテストケース。
    """

    def test_upload_valid_csv_file(self):
        """
        有効なCSVファイルをアップロードするテスト。
        """
        self.login_and_access_upload_shifts()

        # テスト用のCSVファイルを作成
        csv_content = "date,employee_number,start_time,end_time,break_time\n2023/11/01,1,09:00,17:00,01:00:00\n"
        csv_file = SimpleUploadedFile(
            "valid_shifts.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # アップロード処理を実行
        response = self.client.post(reverse('upload_shifts'), {'csv_file': csv_file}, follow=True)

        # アップロード成功メッセージを確認
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "1 件のシフトが正常にアップロードされました。")

    def test_upload_csv_with_invalid_user(self):
        """
        存在しないユーザーのデータを含むCSVファイルをアップロードするテスト。
        """
        self.login_and_access_upload_shifts()

        # テスト用のCSVファイルを作成（存在しないemployee_numberを含む）
        csv_content = "date,employee_number,start_time,end_time,break_time\n2023/11/01,9999,09:00,17:00,01:00:00\n"
        csv_file = SimpleUploadedFile(
            "invalid_user_shifts.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # アップロード処理を実行
        response = self.client.post(reverse('upload_shifts'), {'csv_file': csv_file}, follow=True)

        # エラーメッセージを確認
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ユーザー 9999 が見つかりません。")

    def test_upload_csv_with_invalid_date_format(self):
        """
        無効な日付形式のデータを含むCSVファイルをアップロードするテスト。
        """
        self.login_and_access_upload_shifts()

        # テスト用のCSVファイルを作成（無効な日付形式を含む）
        csv_content = "date,employee_number,start_time,end_time,break_time\n11-01-2023,1,09:00,17:00,01:00:00\n"
        csv_file = SimpleUploadedFile(
            "invalid_date_shifts.csv",
            csv_content.encode('utf-8'),
            content_type="text/csv"
        )

        # アップロード処理を実行
        response = self.client.post(reverse('upload_shifts'), {'csv_file': csv_file}, follow=True)

        # 日付形式のエラーメッセージを確認
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "エラーが発生しました")
