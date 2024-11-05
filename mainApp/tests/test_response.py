# test_response.py

from django.test import Client
c = Client()

# POSTリクエストの例
response = c.post("/homePage/", {"user_id": "test01@test.com", "password": "asdqwe"})
assert response.status_code == 200  # ステータスコードが200（成功）か確認

# GETリクエストの例
response = c.get("/homePage/")
assert b'<!DOCTYPE html' in response.content  # レスポンスのコンテンツに特定の内容が含まれているか確認
