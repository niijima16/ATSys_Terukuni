#!/bin/bash

# Wait for the database to be ready
while ! nc -z db 3306; do
  echo "Waiting for MySQL database to start..."
  sleep 1
done
echo "MySQL database is ready!"

# マイグレーションを実行
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Djangoサーバーを起動
python manage.py runserver 0.0.0.0:8000
